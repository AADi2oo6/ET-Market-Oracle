with open("full_output.txt", "rb") as f:
    text = f.read().decode("utf-16", errors="ignore")
    print(text[-2000:])
