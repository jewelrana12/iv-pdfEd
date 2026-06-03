import fitz
import os
import tkinter as tk
from tkinter import filedialog, messagebox

FONT_NAME = "helv"
FONT_SIZE = 8
PADDING_X = 3

OLD_VISA = "MISCELLANEOUS VISA"
NEW_VISA = "DOUBLE ENTRY"


# -----------------------------
# PROCESS PDF (ONE RECORD)
# -----------------------------
def process_single_pdf(info_row, pdf_file):

    GIVEN_NAME, SURNAME, PASSPORT, PHONE, EMAIL = info_row

    NEW_VALUES = {
        "Surname (As in Passport)": SURNAME,
        "Given Name (As in Passport)": GIVEN_NAME,
        "Passport No.": PASSPORT,
        "Phone No": PHONE,
        "Email address": EMAIL,
    }

    doc = fitz.open(pdf_file)

    for page in doc:

        all_hits = []

        # ---------------- NORMAL FIELDS ----------------
        for label, new_value in NEW_VALUES.items():
            label_rects = page.search_for(label)

            for rect in label_rects:
                row_height = rect.height

                value_rect = fitz.Rect(
                    rect.x1 + PADDING_X,
                    rect.y0,
                    rect.x1 + 250,
                    rect.y0 + row_height
                )

                page.add_redact_annot(value_rect, fill=(1, 1, 1))

                text_x = value_rect.x0 + 2
                text_y = value_rect.y0 + (row_height / 2) + 3

                all_hits.append((text_x, text_y, new_value))

        # ---------------- VISA FIELD ----------------
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

        page.apply_redactions()

        for x, y, value in all_hits:
            page.insert_text(
                (x, y),
                value,
                fontname=FONT_NAME,
                fontsize=FONT_SIZE,
                color=(0, 0, 0),
            )

    output = "edited_" + os.path.basename(pdf_file)
    doc.save(output)
    doc.close()

    return output


# -----------------------------
# PROCESS ALL
# -----------------------------
def process_all(info_path, pdf_files):

    with open(info_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    records = [line.split(",") for line in lines]

    if len(records) != len(pdf_files):
        messagebox.showerror(
            "Error",
            f"Mismatch!\nInfo rows: {len(records)}\nPDF files: {len(pdf_files)}"
        )
        return

    pdf_files = sorted(pdf_files)

    outputs = []

    for i in range(len(pdf_files)):
        out = process_single_pdf(records[i], pdf_files[i])
        outputs.append(out)

    messagebox.showinfo("Done", f"Processed {len(outputs)} PDFs successfully!")


# -----------------------------
# GUI
# -----------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("IVAC Multi PDF Editor")
        self.root.geometry("500x260")

        self.info_file = ""
        self.pdf_files = []

        tk.Button(root, text="Select Info File", command=self.select_info).pack(pady=10)
        self.lbl1 = tk.Label(root, text="No file selected")
        self.lbl1.pack()

        tk.Button(root, text="Select PDF Files", command=self.select_pdf).pack(pady=10)
        self.lbl2 = tk.Label(root, text="No PDFs selected")
        self.lbl2.pack()

        tk.Button(root, text="Generate", bg="black", fg="white", command=self.run).pack(pady=20)

    def select_info(self):
        file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file:
            self.info_file = file
            self.lbl1.config(text=file)

    def select_pdf(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if files:
            self.pdf_files = list(files)
            self.lbl2.config(text=f"{len(files)} PDFs selected")

    def run(self):
        if not self.info_file or not self.pdf_files:
            messagebox.showwarning("Warning", "Select both files")
            return

        process_all(self.info_file, self.pdf_files)


# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()