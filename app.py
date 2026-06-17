from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Global DataFrames
df_original = None
df_display = None

# Columns to display on screen
DISPLAY_COLUMNS = [
    "INVALID_COLUMNS",
    "COURSE_NAME",
    "YEAR",
    "CSV_MONTH",
    
    "SEM",
    "REGN_NO"
]


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    global df_original, df_display

    file = request.files['csvfile']

    if file.filename == '':
        return "No file selected"

    try:
        # Read uploaded CSV
        df_original = pd.read_csv(file, dtype=str)

        # Display only required columns if they exist
        available_display_columns = [
            col for col in DISPLAY_COLUMNS
            if col in df_original.columns
        ]

        if len(available_display_columns) == 0:
            return "Required display columns not found in CSV."

        df_display = df_original[available_display_columns]

        return render_template(
            'display.html',
            columns=df_display.columns,
            data=df_display.fillna("").to_dict('records')
        )

    except Exception as e:
        return f"Error reading CSV: {str(e)}"


@app.route('/save', methods=['POST'])
def save():
    global df_original

    selected_rows = request.form.getlist('row')

    if not selected_rows:
        return "No rows selected"

    selected_indices = [int(i) for i in selected_rows]

    # Selected records from original CSV
    selected_df = df_original.iloc[selected_indices]

    # Fixed columns to save
    base_columns = [
        "INVALID_COLUMNS",
        "ACADEMIC_COURSE_ID",
        "REGN_NO",
        "CNAME",
        "GENDER",
        "DOB",
        "MOBILE",
        "FNAME",
        "SEM",
        "MRKS_REC_STATUS",
        "RESULT",
        "YEAR",
        "CSV_MONTH",
        "TOT",
        "TOT_MAX",
        "TOT_MIN",
        "TOT_MRKS"
    ]

    # Automatically include all subject columns
    sub_columns = [
        col for col in selected_df.columns
        if col.startswith("SUB")
    ]

    # Combine columns
    save_columns = []

    for col in base_columns + sub_columns:
        if col in selected_df.columns:
            save_columns.append(col)

    # Keep only required columns
    selected_df = selected_df[save_columns]

    # Output Excel file
    output_file = "save_the_record.xlsx"

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Append data if file exists
    if os.path.exists(output_file):
        try:
            existing_df = pd.read_excel(
                output_file,
                dtype=str
            )

            final_df = pd.concat(
                [existing_df, selected_df],
                ignore_index=True,
                sort=False
            )

        except Exception:
            final_df = selected_df

    else:
        final_df = selected_df

    # Save Excel
    final_df.to_excel(
        output_file,
        index=False,
        engine="openpyxl"
    )

    return f"""
    <html>
    <head>
        <title>Saved Successfully</title>
    </head>
    <body style="font-family:Arial;text-align:center;padding-top:50px;">
    
        <h2 style="color:green;">
            Records Saved Successfully
        </h2>

        <p>
            <b>{len(selected_indices)}</b> record(s) saved.
        </p>

        <p>
            Saved File:
        </p>

        <p style="color:blue;">
            {output_file}
        </p>

        <br>

        <a href="/">
            Upload Another File
        </a>

    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)