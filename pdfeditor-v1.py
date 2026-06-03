import fitz
import os

# -----------------------------
# FONT CONFIG
# -----------------------------
FONT_NAME = "helv"
FONT_SIZE = 8

# padding inside value column
PADDING_X = 3
PADDING_Y = 0

# -----------------------------
# INPUT DATA
# -----------------------------
with open("info.txt", "r", encoding="utf-8") as f:
    line = f.read().strip()

GIVEN_NAME, SURNAME, PASSPORT, PHONE, EMAIL = line.split(",")

NEW_VALUES = {
    "Surname (As in Passport)": SURNAME,
    "Given Name (As in Passport)": GIVEN_NAME,
    "Passport No.": PASSPORT,
    "Phone No": PHONE,
    "Email address": EMAIL,
}

OLD_VISA = "MISCELLANEOUS VISA"
NEW_VISA = "DOUBLE ENTRY"

# -----------------------------
# PROCESS PDFs
# -----------------------------
for pdf_file in os.listdir("."):
    if not pdf_file.lower().endswith(".pdf"):
        continue

    doc = fitz.open(pdf_file)

    for page in doc:

        all_hits = []

        # -----------------------------
        # NORMAL FIELDS (COLUMN ALIGNMENT)
        # -----------------------------
        for label, new_value in NEW_VALUES.items():
            label_rects = page.search_for(label)

            for rect in label_rects:

                # 👉 define full row height
                row_height = rect.height

                # 👉 create VALUE COLUMN rectangle (right side)
                value_rect = fitz.Rect(
                    rect.x1 + PADDING_X,
                    rect.y0,
                    rect.x1 + 250,   # width of value column
                    rect.y0 + row_height
                )

                page.add_redact_annot(value_rect, fill=(1, 1, 1))

                # store center position for perfect alignment
                text_x = value_rect.x0 + 2
                text_y = value_rect.y0 + (row_height / 2) + 3

                all_hits.append((text_x, text_y, new_value))

        # -----------------------------
        # VISA FIELD ONLY
        # -----------------------------
        visa_label_rects = page.search_for("Type Of Visa Required")

        for label_rect in visa_label_rects:

            visa_rects = page.search_for(OLD_VISA)

            for vrect in visa_rects:
                if abs(vrect.y0 - label_rect.y0) < 50:

                    row_height = vrect.height

                    page.add_redact_annot(vrect, fill=(1, 1, 1))

                    text_x = vrect.x0 + 2
                    text_y = vrect.y0 + (row_height / 2) + 3

                    all_hits.append((text_x, text_y, NEW_VISA))

        # -----------------------------
        # APPLY REDACTIONS
        # -----------------------------
        page.apply_redactions()

        # -----------------------------
        # INSERT WITH PERFECT ALIGNMENT
        # -----------------------------
        for x, y, value in all_hits:
            page.insert_text(
                (x, y),
                value,
                fontname=FONT_NAME,
                fontsize=FONT_SIZE,
                color=(0, 0, 0),
            )

    output = "edited_" + pdf_file
    doc.save(output)
    doc.close()

    print("Saved:", output)