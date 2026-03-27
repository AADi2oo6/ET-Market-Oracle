import casparser

def test_local_pdf():
    # Make sure your file is named exactly this in the root folder
    filename = "statement.pdf" 
    password = "202510"

    print(f"🔍 Attempting to parse '{filename}' with password '{password}'...")

    try:
        # casparser can read directly from a file path string
        data = casparser.read_cas_pdf(filename, password)

        print("\n✅ SUCCESS! File parsed correctly.")
        print("=" * 40)
        
        # Print Investor Info
        print(f"👤 Investor Name: {data.investor_info.name}")
        print(f"📧 Email: {data.investor_info.email}")
        
        # Calculate and print total net worth
        total_value = 0
        print("\n📊 Holdings Found:")
        for folio in data.folios:
            for scheme in folio.schemes:
                value = scheme.valuation.value
                total_value += value
                print(f"  - {scheme.scheme} | ₹{value:,.2f}")

        print("=" * 40)
        print(f"💰 Total Portfolio Value: ₹{total_value:,.2f}")
        print("=" * 40)

    except casparser.exceptions.IncorrectPasswordError:
        print("❌ ERROR: Incorrect Password! The password '202510' did not work.")
    except casparser.exceptions.CASParseError as e:
        print(f"❌ ERROR: Failed to parse CAS file. It might not be a 'Detailed' statement. Details: {e}")
    except FileNotFoundError:
        print(f"❌ ERROR: Could not find a file named '{filename}'. Make sure it is in the same folder as this script.")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_local_pdf()