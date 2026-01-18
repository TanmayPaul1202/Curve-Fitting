# Curve Fitting Solver (Flask)

A clean, minimal web app to fit curves to user-provided data:
- Linear: y = a + b x
- Quadratic: y = a + b x + c x^2
- Exponential: y = a e^{b x}
- Logarithmic: y = a + b ln(x)
- Power: y = a x^b

## Quickstart

1) Create a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
pip install -r requirements.txt
```

3) Run the app:

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Notes
- Exponential and power fits require y > 0 (log transform).
- Logarithmic and power fits require x > 0 (log transform).
- Best fit is chosen by highest R² among successful fits.

Here is a Screenshot :

<img width="1893" height="910" alt="Screenshot 2025-12-29 123857" src="https://github.com/user-attachments/assets/d7cee5c9-4763-4dc0-ac80-34dd39a4ac45" />
<img width="1898" height="917" alt="Screenshot 2025-12-29 123836" src="https://github.com/user-attachments/assets/7f633f45-6c04-4dbd-929a-2f46b91ba6aa" />
<img width="1919" height="922" alt="Screenshot 2025-12-29 123736" src="https://github.com/user-attachments/assets/7807f53c-dd8a-4116-b44a-9440ce653965" />
<img width="1896" height="913" alt="Screenshot 2025-12-29 124108" src="https://github.com/user-attachments/assets/90758716-9331-490f-bf51-7acb09009954" />
<img width="1895" height="908" alt="Screenshot 2025-12-29 124052" src="https://github.com/user-attachments/assets/1e41595f-2633-49e4-9722-eaabd7f9521d" />
<img width="1894" height="905" alt="Screenshot 2025-12-29 124031" src="https://github.com/user-attachments/assets/c4489e99-dda2-4b74-ad35-64001d1e187d" />
<img width="1895" height="915" alt="Screenshot 2025-12-29 124011" src="https://github.com/user-attachments/assets/b28df6ca-c414-4015-835d-501b8901c66b" />
<img width="1896" height="914" alt="Screenshot 2025-12-29 123952" src="https://github.com/user-attachments/assets/22a94794-efb5-4445-b7b0-5b360782aa5e" />
<img width="1900" height="919" alt="Screenshot 2025-12-29 123938" src="https://github.com/user-attachments/assets/3222d4b8-fff5-4531-ac89-459b64830895" />
<img width="1896" height="913" alt="Screenshot 2025-12-29 123920" src="https://github.com/user-attachments/assets/958c465b-e0fe-46d7-89ad-eacc5926aacc" />


