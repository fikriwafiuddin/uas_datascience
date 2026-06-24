"""
Flask Web Application for Rice Production Prediction
Aplikasi Web untuk Prediksi Produksi Padi Menggunakan Regresi Linier
"""

from flask import Flask, render_template, request, session
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import io

app = Flask(__name__)
app.secret_key = 'regression-app-secret-key-change-in-production'

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB file upload

# Model parameters dari training yang sudah dilakukan
# Koefisien untuk Luas Panen (ha) dan Produktivitas (ku/ha)
COEF_LUAS_PANEN = 5.56836114
COEF_PRODUKTIVITAS = 7492.31789
INTERCEPT = -420125.065542602


def predict_production(luas_panen, produktivitas):
    """
    Memprediksi produksi padi menggunakan model regresi linier

    Rumus regresi:
    y = 5.56836114 * Luas Panen + 7492.31789 * Produktivitas - 420125.065542602
    """
    y = COEF_LUAS_PANEN * luas_panen + COEF_PRODUKTIVITAS * produktivitas + INTERCEPT
    return y


@app.route('/', methods=['GET', 'POST'])
def index():
    """Halaman utama dengan form input dan hasil prediksi"""
    prediction = None
    luas_panen_input = None
    produktivitas_input = None
    error = None

    if request.method == 'POST':
        try:
            luas_panen_input = request.form.get('luas_panen')
            produktivitas_input = request.form.get('produktivitas')

            if not luas_panen_input or not produktivitas_input:
                error = "Mohon isi kedua nilai (Luas Panen dan Produktivitas)"
            else:
                luas_panen = float(luas_panen_input)
                produktivitas = float(produktivitas_input)

                if luas_panen < 0 or produktivitas < 0:
                    error = "Nilai tidak boleh negatif"
                else:
                    prediction = predict_production(luas_panen, produktivitas)

        except ValueError:
            error = "Masukkan angka yang valid"

    regression_equation = (
        f"y = {COEF_LUAS_PANEN} × Luas Panen (ha) + {COEF_PRODUKTIVITAS} "
        f"× Produktivitas (ku/ha) {INTERCEPT}"
    )

    return render_template(
        'index.html',
        prediction=prediction,
        luas_panen=luas_panen_input,
        produktivitas=produktivitas_input,
        error=error,
        regression_equation=regression_equation,
        coef_luas=COEF_LUAS_PANEN,
        coef_prod=COEF_PRODUKTIVITAS,
        intercept=INTERCEPT
    )


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint untuk prediksi"""
    from flask import jsonify

    try:
        data = request.get_json()
        luas_panen = float(data.get('luas_panen', 0))
        produktivitas = float(data.get('produktivitas', 0))

        prediction = predict_production(luas_panen, produktivitas)

        return jsonify({
            'success': True,
            'prediction': prediction,
            'luas_panen': luas_panen,
            'produktivitas': produktivitas
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ==================== FITUR REGRESI LINIER BERGANDA CUSTOM ====================

@app.route('/custom-regression', methods=['GET', 'POST'])
def custom_regression():
    """
    Halaman untuk regresi linier berganda dengan upload file CSV/Excel.
    Alur:
    1. Upload file CSV/Excel
    2. Pilih kolom untuk X1, X2, ..., Y dari dropdown
    3. Latih model
    4. Lakukan prediksi
    """

    error = None
    success_message = None
    model_trained = False
    regression_equation = None
    model_stats = None
    prediction_result = None
    data_preview = None
    column_names = None

    if request.method == 'POST':
        action = request.form.get('action')

        # STEP 1: Upload dan parse file
        if action == 'upload':
            try:
                if 'file' not in request.files:
                    error = "Tidak ada file yang diupload"
                else:
                    file = request.files['file']

                    if file.filename == '':
                        error = "Tidak ada file yang dipilih"
                    else:
                        # Baca file berdasarkan ekstensi
                        filename = file.filename.lower()

                        if filename.endswith('.csv'):
                            # Baca CSV
                            df = pd.read_csv(file)
                        elif filename.endswith(('.xlsx', '.xls')):
                            # Baca Excel
                            df = pd.read_excel(file)
                        else:
                            error = "Format file harus CSV atau Excel (.xlsx, .xls)"
                            return render_template('custom_regression.html', error=error)

                        # Simpan dataframe ke session
                        session['csv_data'] = df.to_csv(index=False)
                        session['column_names'] = df.columns.tolist()

                        # Tampilkan preview data (5 baris pertama)
                        data_preview = df.head(5).values.tolist()
                        column_names = df.columns.tolist()

                        success_message = f"File berhasil diupload! Terdapat {len(df)} baris dan {len(df.columns)} kolom."

            except Exception as e:
                error = f"Error membaca file: {str(e)}"

        # STEP 2: Train model dengan kolom yang dipilih
        elif action == 'train':
            try:
                # Ambil data dari session
                if 'csv_data' not in session:
                    error = "Session expired. Silakan upload file kembali."
                else:
                    df = pd.read_csv(io.StringIO(session['csv_data']))
                    column_names = session.get('column_names', [])

                    # Ambil pilihan kolom dari form
                    x_columns = request.form.getlist('x_columns')
                    y_column = request.form.get('y_column')

                    if not x_columns or not y_column:
                        error = "Mohon pilih minimal 1 kolom X dan 1 kolom Y"
                    elif y_column in x_columns:
                        error = "Kolom Y tidak boleh sama dengan kolom X"
                    else:
                        # Validasi jumlah data
                        if len(df) < 2:
                            error = "Minimal diperlukan 2 baris data untuk regresi"
                        else:
                            # Siapkan data
                            X_train = df[x_columns].values
                            y_train = df[y_column].values

                            # Train model
                            model = LinearRegression()
                            model.fit(X_train, y_train)

                            # Calculate R-squared
                            y_pred = model.predict(X_train)
                            ss_res = np.sum((y_train - y_pred) ** 2)
                            ss_tot = np.sum((y_train - np.mean(y_train)) ** 2)
                            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

                            # Simpan model ke session
                            session['model_coef'] = model.coef_.tolist()
                            session['model_intercept'] = float(model.intercept_)
                            session['x_columns'] = x_columns
                            session['y_column'] = y_column
                            session['n_features'] = len(x_columns)

                            # Buat persamaan regresi
                            equation_parts = []
                            for i, (col_name, coef) in enumerate(zip(x_columns, model.coef_)):
                                if coef >= 0:
                                    equation_parts.append(f"{coef:.6f} × {col_name}")
                                else:
                                    equation_parts.append(f"- {abs(coef):.6f} × {col_name}")

                            if model.intercept_ >= 0:
                                regression_equation = f"{y_column} = " + " + ".join(equation_parts) + f" + {model.intercept_:.6f}"
                            else:
                                regression_equation = f"{y_column} = " + " + ".join(equation_parts) + f" - {abs(model.intercept_):.6f}"

                            # Model statistics
                            model_stats = {
                                'r_squared': r_squared,
                                'n_samples': len(X_train),
                                'n_features': len(x_columns),
                                'coef_dict': dict(zip(x_columns, model.coef_)),
                                'intercept': model.intercept_,
                                'x_columns': x_columns,
                                'y_column': y_column
                            }

                            # Preview data untuk display
                            data_preview = df.head(5).values.tolist()
                            column_names = df.columns.tolist()

                            model_trained = True
                            success_message = "Model berhasil dilatih! Anda sekarang dapat melakukan prediksi."

            except Exception as e:
                error = f"Error dalam melatih model: {str(e)}"

        # STEP 3: Prediksi
        elif action == 'predict':
            try:
                # Cek apakah model sudah dilatih
                if 'model_coef' not in session:
                    error = "Silakan latih model terlebih dahulu"
                else:
                    # Ambil parameter model dari session
                    coef = np.array(session.get('model_coef', []))
                    intercept = session.get('model_intercept', 0)
                    x_columns = session.get('x_columns', [])
                    y_column = session.get('y_column', 'Y')
                    n_features = session.get('n_features', 2)

                    # Parse input prediksi
                    prediction_inputs = {}
                    for col in x_columns:
                        val = request.form.get(f'pred_{col}', '')
                        if not val:
                            error = f"Mohon isi nilai untuk {col}"
                            break
                        prediction_inputs[col] = float(val)

                    if not error:
                        # Hitung prediksi
                        input_values = [prediction_inputs[col] for col in x_columns]
                        input_array = np.array(input_values).reshape(1, -1)
                        prediction = np.dot(input_array, coef) + intercept

                        prediction_result = {
                            'value': float(prediction[0]),
                            'inputs': prediction_inputs,
                            'x_columns': x_columns,
                            'y_column': y_column
                        }

                        # Rebuild equation for display
                        equation_parts = []
                        for col_name, c in zip(x_columns, coef):
                            if c >= 0:
                                equation_parts.append(f"{c:.6f} × {col_name}")
                            else:
                                equation_parts.append(f"- {abs(c):.6f} × {col_name}")

                        if intercept >= 0:
                            regression_equation = f"{y_column} = " + " + ".join(equation_parts) + f" + {intercept:.6f}"
                        else:
                            regression_equation = f"{y_column} = " + " + ".join(equation_parts) + f" - {abs(intercept):.6f}"

                        model_trained = True

                        # Get data preview
                        if 'csv_data' in session:
                            df = pd.read_csv(io.StringIO(session['csv_data']))
                            data_preview = df.head(5).values.tolist()
                            column_names = df.columns.tolist()

            except Exception as e:
                error = f"Error dalam prediksi: {str(e)}"

        # Reset model
        elif action == 'reset':
            for key in ['model_coef', 'model_intercept', 'x_columns', 'y_column', 'n_features']:
                session.pop(key, None)
            success_message = "Model telah di-reset. Silakan upload file baru."

    # Jika ada data di session, tampilkan preview
    if not data_preview and 'csv_data' in session:
        try:
            df = pd.read_csv(io.StringIO(session['csv_data']))
            data_preview = df.head(5).values.tolist()
            column_names = session.get('column_names', df.columns.tolist())
        except:
            pass

    # Get model stats from session if available
    if not model_stats and 'model_coef' in session:
        x_columns = session.get('x_columns', [])
        model_coef = session.get('model_coef', [])
        model_stats = {
            'r_squared': 0,  # Not stored in session
            'n_samples': 0,
            'n_features': session.get('n_features', 0),
            'coef_dict': dict(zip(x_columns, model_coef)) if x_columns and model_coef else {},
            'intercept': session.get('model_intercept', 0),
            'x_columns': x_columns,
            'y_column': session.get('y_column', 'Y')
        }

    return render_template(
        'custom_regression.html',
        error=error,
        success_message=success_message,
        model_trained=model_trained,
        regression_equation=regression_equation,
        model_stats=model_stats,
        prediction_result=prediction_result,
        data_preview=data_preview,
        column_names=column_names
    )


@app.route('/reset-session', methods=['POST'])
def reset_session():
    """Reset semua session data"""
    for key in list(session.keys()):
        session.pop(key, None)
    from flask import redirect, url_for
    return redirect(url_for('custom_regression'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
