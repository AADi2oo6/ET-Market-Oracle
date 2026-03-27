from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Header
from sqlalchemy.orm import Session
import casparser
import jwt
import traceback
import io
import os
import shutil
from typing import Optional

from app.core.database import get_db
from app.models.schema import User, Holding
from app.core.security import SECRET_KEY, ALGORITHM

portfolio_router = APIRouter()

def get_current_user_optional(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Optional dependency to identify user if a token is present, otherwise return None."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        return db.query(User).filter(User.id == user_id).first()
    except jwt.PyJWTError:
        return None

@portfolio_router.post("/upload")
async def upload_portfolio(
    file: UploadFile = File(...),
    password: str = Form(...),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    try:
        # Save the uploaded file to disk
        os.makedirs("cas_docs", exist_ok=True)
        file_path = f"cas_docs/{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse PDF using casparser
        try:
            casdata = casparser.read_cas_pdf(file_path, password)
        except casparser.exceptions.IncorrectPasswordError as e:
            traceback.print_exc()
            raise HTTPException(status_code=400, detail="Incorrect PDF Password. Try your PAN card number in ALL CAPS.")
        except casparser.exceptions.CASParseError as e:
            traceback.print_exc()
            raise HTTPException(status_code=400, detail="Invalid CAS File. Ensure you downloaded a 'Detailed Consolidated Account Statement'.")
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=400, detail=f"Raw Error: {str(e)}")

        extracted_holdings = []
        
        for folio in casdata.folios:
            for scheme in folio.schemes:
                # We only want schemes with a positive balance/valuation
                if scheme.valuation.value > 0:
                    holding_data = {
                        "scheme_name": scheme.scheme,
                        "folio_number": folio.folio,
                        "units": scheme.close,
                        "current_value": scheme.valuation.value,
                    }
                    extracted_holdings.append(holding_data)
        
        # If user is logged in, sync to database
        if current_user:
            # Delete old holdings
            db.query(Holding).filter(Holding.user_id == current_user.id).delete()
            
            # Insert new holdings
            for h in extracted_holdings:
                db_holding = Holding(
                    user_id=current_user.id,
                    scheme_name=h["scheme_name"],
                    folio_number=h["folio_number"],
                    units=h["units"],
                    current_value=h["current_value"]
                )
                db.add(db_holding)
            
            db.commit()

        return {"status": "success", "holdings": extracted_holdings}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
