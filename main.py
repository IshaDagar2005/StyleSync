import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from dbconfig import connect_db

# Global
current_user = None
user_inputs = {}

class StyleSyncApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StyleSync - Body Shape Identifier")
        self.geometry("800x600")
        self.frames = {}
        self.create_tables()

        for F in (LoginPage, InstructionsPage, FrontShapePage, SideShapePage, ShoulderShapePage, ResultPage):
            page = F(parent=self, controller=self)
            self.frames[F] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

    def create_tables(self):
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE,
                password VARCHAR(100)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS body_shapes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username INT,
                name VARCHAR(100),
                front_shape CHAR(1),
                side_shape CHAR(2),
                shoulder_shape CHAR(1),
                style_tips TEXT,
                FOREIGN KEY(username) REFERENCES users(id)
            )
        """)
        db.commit()
        db.close()

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Container frame to center everything
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")  # Center the container

        # Title
        tk.Label(container, text="Login / Sign Up", font=("Arial", 24, "bold")).pack(pady=20)

        # Form Section
        form_frame = tk.Frame(container)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Username", font=("Arial", 12)).grid(row=0, column=0, pady=5, sticky="e")
        self.username_entry = tk.Entry(form_frame, font=("Arial", 12), width=25)
        self.username_entry.grid(row=0, column=1, pady=5, padx=10)

        tk.Label(form_frame, text="Password", font=("Arial", 12)).grid(row=1, column=0, pady=5, sticky="e")
        self.password_entry = tk.Entry(form_frame, show="*", font=("Arial", 12), width=25)
        self.password_entry.grid(row=1, column=1, pady=5, padx=10)

        # Buttons Section
        btn_frame = tk.Frame(container)
        btn_frame.pack(pady=15)

        login_btn = tk.Button(btn_frame, text="Login", font=("Arial", 12), width=10, command=self.login_user)
        login_btn.grid(row=0, column=0, padx=10)

        signup_btn = tk.Button(btn_frame, text="Sign Up", font=("Arial", 12), width=10, command=self.register_user)
        signup_btn.grid(row=0, column=1, padx=10)

    def login_user(self):
        global current_user
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()
        db.close()

        if result:
            current_user = username
            self.controller.show_frame(InstructionsPage)
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")

    def register_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            messagebox.showinfo("Success", "Registered successfully. Now login.")
        except:
            messagebox.showerror("Error", "Username already exists.")
        db.close()

class InstructionsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        instructions = (
            "1)You will be asked questions regarding your body shape from front and side view.\n"
            "2)It is advised to click 2 pictures of yourself in tight-fitted clothes and in a clear background\n"
            "to easily analyze your body while attempting the quiz. \n\nThis will increase the accuracy rate of the final result."
        )
        tk.Label(self, text="Instructions", font=("Arial", 24)).pack(pady=20)
        tk.Label(self, text=instructions, wraplength=800, justify="left",font=("Arial",14)).pack(pady=30)
        tk.Button(self, text="Next", font=("Arial", 14), width=4, command=lambda: controller.show_frame(FrontShapePage)).pack()

class FrontShapePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Select Your Front Shape", font=("Arial", 16, "bold")).pack(pady=(10, 5))
        tk.Label(self, text="Compare the width of bust, waist and hip in the front view photo of your body.\nChoose the option that is the closest to your body shape.", wraplength=800, font=("Arial", 12)).pack(pady=(0, 20))
        self.controller = controller
        self.var = tk.StringVar()
        self.build_options("front", ["H", "X", "A", "Y"])
        descriptions = "H: Straight body with minimal curves\nX: Balanced bust and hips with a defined waist\nA: Wider hips compared to shoulders\nY: Broad shoulders with narrow hips"
        tk.Label(self, text=descriptions , wraplength=800, font=("Arial", 10)).pack(pady=(0, 20))
        tk.Button(self, text="Next", command=self.save_and_next).pack(pady=10)

    def build_options(self, folder, codes):
        for code in codes:
            frame = tk.Frame(self)
            frame.pack(pady=5)
            path = os.path.join("image", folder, f"{code}.jpg")
            img = Image.open(path).resize((100, 100))
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(frame, image=photo)
            lbl.image = photo
            lbl.pack(side="left", padx=10)
            tk.Radiobutton(frame, text=code, variable=self.var, value=code).pack(side="left")

    def save_and_next(self):
        choice = self.var.get()
        if not choice:
            messagebox.showwarning("Input Required", "Please select your front shape.")
            return
        user_inputs["front"] = choice
        self.controller.show_frame(SideShapePage)

class SideShapePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.var = tk.StringVar()
        tk.Label(self, text="Select Your Side Shape", font=("Arial", 14)).pack(pady=10)
        self.build_options("side", ["b_", "P", "B", "I", "d"])
        tk.Button(self, text="Next", command=self.save_and_next).pack(pady=10)

    def build_options(self, folder, codes):
        for code in codes:
            frame = tk.Frame(self)
            frame.pack(pady=5)
            path = os.path.join("image", folder, f"{code}.jpg")
            img = Image.open(path).resize((100, 100))
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(frame, image=photo)
            lbl.image = photo
            lbl.pack(side="left", padx=10)
            tk.Radiobutton(frame, text=code, variable=self.var, value=code).pack(side="left")

    def save_and_next(self):
        choice = self.var.get()
        if not choice:
            messagebox.showwarning("Input Required", "Please select your side shape.")
            return
        user_inputs["side"] = choice
        self.controller.show_frame(ShoulderShapePage)

class ShoulderShapePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.var = tk.StringVar()
        tk.Label(self, text="Select Your Shoulder Shape", font=("Arial", 14)).pack(pady=10)
        self.build_options("shoulder", ["T", "n", "Nm"])
        tk.Label(self, text="Enter Your Name").pack()
        self.name_entry = tk.Entry(self)
        self.name_entry.pack(pady=5)
        tk.Button(self, text="Get My Results", command=self.show_result).pack(pady=10)

    def build_options(self, folder, codes):
        for code in codes:
            frame = tk.Frame(self)
            frame.pack(pady=5)
            path = os.path.join("image", folder, f"{code}.jpg")
            img = Image.open(path).resize((100, 100))
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(frame, image=photo)
            lbl.image = photo
            lbl.pack(side="left", padx=10)
            tk.Radiobutton(frame, text=code, variable=self.var, value=code).pack(side="left")

    def show_result(self):
        name = self.name_entry.get()
        shoulder = self.var.get()
        if not (name and shoulder):
            messagebox.showwarning("Input Required", "Please enter name and select shoulder shape.")
            return
        user_inputs["name"] = name
        user_inputs["shoulder"] = shoulder
        self.controller.frames[ResultPage].render()
        self.controller.show_frame(ResultPage)

class ResultPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Title
        tk.Label(self, text="Your Personalized Style Tips", font=("Arial", 18, "bold")).pack(pady=20)

        # Result display
        self.result_label = tk.Label(
            self,
            text="",
            wraplength=700,
            justify="left",
            font=("Arial", 12)
        )
        self.result_label.pack(pady=20, expand=True)

        # Back to Home Button
        tk.Button(
            self,
            text="Back to Home",
            font=("Arial", 12),
            command=lambda: controller.show_frame(LoginPage)
        ).pack(pady=10)

    def render(self):
        name = user_inputs.get("name")
        front = user_inputs.get("front")
        side = user_inputs.get("side")
        shoulder = user_inputs.get("shoulder")

        tips = generate_style_tips(front, side, shoulder)
        if not tips.strip():
            tips = "No style tips available. Please recheck your inputs."

        save_to_db(name, front, side, shoulder, tips)
        self.result_label.config(
            text=f"Hi {name},\n\nHere are your personalized tips:\n\n{tips}"
        )


def generate_style_tips(front, side, shoulder):
    tips = []
    if front == "H":
        tips.append("Add volume around your waist with belts or peplum tops.")
    elif front == "X":
        tips.append("Highlight your waist with fit-and-flare or wrap dresses.")
    elif front == "A":
        tips.append("Use structured tops and details on upper body.")
    elif front == "Y":
        tips.append("Wear darker tops and flared bottoms to balance shape.")

    if "b" in side:
        tips.append("Avoid clingy tops. Use high-rise pants to tuck belly.")
    if "P" in side:
        tips.append("Use V-necks and avoid excessive chest detail.")
    if "B" in side:
        tips.append("Choose clean silhouettes and avoid bulky layers.")
    if "d" in side:
        tips.append("Show off curves with fitted dresses or pencil skirts.")

    if shoulder == "T":
        tips.append("Avoid shoulder pads. Use soft fabrics on top.")
    elif shoulder == "n":
        tips.append("Use puff sleeves or shoulder detailing to balance.")

    return "\n- " + "\n- ".join(tips)

def save_to_db(name, front, side, shoulder, tips):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE username=%s", (current_user,))
    username = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO body_shapes (username, name, front_shape, side_shape, shoulder_shape, style_tips)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (username, name, front, side, shoulder, tips))
    db.commit()
    db.close()

if __name__ == "__main__":
    app = StyleSyncApp()
    app.mainloop()
