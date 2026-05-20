import tkinter as tk
from tkinter import ttk, messagebox

from managers.file_manager import FileManager
from managers.rental_manager import RentalManager


# Catppuccin Mocha color palette
COLORS = {
    "bg":        "#1e1e2e",
    "surface":   "#313244",
    "overlay":   "#45475a",
    "text":      "#cdd6f4",
    "subtext":   "#a6adc8",
    "yellow":    "#f9e2af",
    "green":     "#a6e3a1",
    "red":       "#f38ba8",
    "blue":      "#89b4fa",
    "mauve":     "#cba6f7",
    "peach":     "#fab387",
}


class CarRentalApp:
    def __init__(self, root):
        self.root = root
        self.manager = RentalManager()
        self.manager.cars = FileManager.load_cars()

        self._setup_window()
        self._setup_styles()
        self._build_layout()
        self.refresh_cars()

    def _setup_window(self):
        self.root.title("Car Rental System")
        self.root.geometry("980x620")
        self.root.minsize(820, 520)
        self.root.configure(bg=COLORS["bg"])

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=COLORS["surface"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["surface"],
            rowheight=34,
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["overlay"],
            foreground=COLORS["yellow"],
            font=("Segoe UI", 11, "bold"),
            borderwidth=0,
            relief="flat",
            padding=8,
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["blue"])],
            foreground=[("selected", COLORS["bg"])],
        )
        style.map("Treeview.Heading", background=[("active", COLORS["overlay"])])

        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["surface"],
            troughcolor=COLORS["bg"],
            bordercolor=COLORS["bg"],
            arrowcolor=COLORS["text"],
        )

    def _build_layout(self):
        # ---------- Header ----------
        header = tk.Frame(self.root, bg=COLORS["bg"])
        header.pack(fill="x", padx=24, pady=(22, 8))

        tk.Label(
            header,
            text="CAR RENTAL SYSTEM",
            bg=COLORS["bg"],
            fg=COLORS["yellow"],
            font=("Segoe UI", 24, "bold"),
        ).pack(side="left")

        self.stats_label = tk.Label(
            header,
            text="",
            bg=COLORS["bg"],
            fg=COLORS["subtext"],
            font=("Segoe UI", 11),
        )
        self.stats_label.pack(side="right")

        # Subtitle / hint
        tk.Label(
            self.root,
            text="Select a car from the list, then choose an action below.",
            bg=COLORS["bg"],
            fg=COLORS["subtext"],
            font=("Segoe UI", 10, "italic"),
        ).pack(anchor="w", padx=26)

        # ---------- Table ----------
        table_wrap = tk.Frame(self.root, bg=COLORS["bg"])
        table_wrap.pack(fill="both", expand=True, padx=24, pady=14)

        columns = ("id", "brand", "model", "year", "price", "status")
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings")

        headings = [
            ("id",     "ID",        60,  "center"),
            ("brand",  "Brand",     160, "w"),
            ("model",  "Model",     160, "w"),
            ("year",   "Year",      90,  "center"),
            ("price",  "Price/day", 130, "center"),
            ("status", "Status",    130, "center"),
        ]
        for key, label, width, anchor in headings:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, anchor=anchor)

        self.tree.tag_configure("available", foreground=COLORS["green"])
        self.tree.tag_configure("rented",    foreground=COLORS["red"])

        scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda _e: self.open_rent_dialog())

        # ---------- Buttons ----------
        btn_bar = tk.Frame(self.root, bg=COLORS["bg"])
        btn_bar.pack(fill="x", padx=24, pady=(8, 22))

        buttons = [
            ("Refresh",     self.refresh_cars,     COLORS["blue"]),
            ("Rent Car",    self.open_rent_dialog, COLORS["green"]),
            ("Return Car",  self.return_car,       COLORS["peach"]),
            ("Statistics",  self.show_statistics,  COLORS["mauve"]),
            ("Exit",        self.root.quit,        COLORS["red"]),
        ]
        for text, command, color in buttons:
            self._make_button(btn_bar, text, command, color).pack(side="left", padx=4)

    def _make_button(self, parent, text, command, color):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=COLORS["bg"],
            activebackground=color,
            activeforeground=COLORS["bg"],
            font=("Segoe UI", 11, "bold"),
            bd=0,
            relief="flat",
            padx=22,
            pady=10,
            cursor="hand2",
            highlightthickness=0,
        )
        btn.bind("<Enter>", lambda _e: btn.config(bg=COLORS["text"]))
        btn.bind("<Leave>", lambda _e: btn.config(bg=color))
        return btn

    # ---------- Actions ----------
    def refresh_cars(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for car in self.manager.cars:
            status = "Available" if car.is_available else "Rented"
            tag = "available" if car.is_available else "rented"
            self.tree.insert(
                "",
                "end",
                values=(
                    car.car_id,
                    car.brand,
                    car.model,
                    car.year,
                    f"${car.price_per_day}",
                    status,
                ),
                tags=(tag,),
            )

        self._update_stats_label()

    def _update_stats_label(self):
        total = len(self.manager.cars)
        available = sum(1 for c in self.manager.cars if c.is_available)
        rented = total - available
        self.stats_label.config(
            text=f"Total: {total}    Available: {available}    Rented: {rented}"
        )

    def _selected_car(self):
        sel = self.tree.selection()
        if not sel:
            return None
        car_id = int(self.tree.item(sel[0])["values"][0])
        return next((c for c in self.manager.cars if c.car_id == car_id), None)

    def open_rent_dialog(self):
        car = self._selected_car()
        if car is None:
            messagebox.showwarning(
                "No selection",
                "Please select a car from the list first.",
            )
            return
        if not car.is_available:
            messagebox.showerror(
                "Not available",
                f"{car.brand} {car.model} is already rented.",
            )
            return

        RentDialog(self.root, car, self._on_rent_confirmed)

    def _on_rent_confirmed(self, car, client_name, days):
        self.manager.rent_car(car.car_id, client_name, days)
        FileManager.save_cars(self.manager.cars)

        total = days * car.price_per_day
        messagebox.showinfo(
            "Success",
            f"Car rented successfully!\n\n"
            f"Car:    {car.brand} {car.model}\n"
            f"Client: {client_name}\n"
            f"Days:   {days}\n"
            f"Total:  ${total}",
        )
        self.refresh_cars()

    def return_car(self):
        car = self._selected_car()
        if car is None:
            messagebox.showwarning(
                "No selection",
                "Please select a car from the list first.",
            )
            return
        if car.is_available:
            messagebox.showinfo(
                "Already available",
                f"{car.brand} {car.model} is not rented.",
            )
            return

        if messagebox.askyesno("Confirm return", f"Return {car.brand} {car.model}?"):
            self.manager.return_car(car.car_id)
            FileManager.save_cars(self.manager.cars)
            messagebox.showinfo("Success", "Car returned successfully.")
            self.refresh_cars()

    def show_statistics(self):
        total = len(self.manager.cars)
        available = sum(1 for c in self.manager.cars if c.is_available)
        rented = total - available
        revenue = sum(b.total_price for b in self.manager.bookings)
        active = len(self.manager.bookings)

        messagebox.showinfo(
            "Statistics",
            f"Total cars:       {total}\n"
            f"Available:        {available}\n"
            f"Rented:           {rented}\n"
            f"Active bookings:  {active}\n"
            f"Revenue (session): ${revenue}",
        )


class RentDialog:
    def __init__(self, parent, car, on_confirm):
        self.car = car
        self.on_confirm = on_confirm

        self.window = tk.Toplevel(parent)
        self.window.title("Rent a Car")
        self.window.configure(bg=COLORS["bg"])
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()

        width, height = 420, 360
        parent.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()  - width)  // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

        self._build()

    def _build(self):
        tk.Label(
            self.window,
            text="RENT A CAR",
            bg=COLORS["bg"],
            fg=COLORS["yellow"],
            font=("Segoe UI", 18, "bold"),
        ).pack(pady=(22, 8))

        info = (
            f"{self.car.brand} {self.car.model}  ({self.car.year})\n"
            f"${self.car.price_per_day} / day"
        )
        tk.Label(
            self.window,
            text=info,
            bg=COLORS["bg"],
            fg=COLORS["subtext"],
            font=("Segoe UI", 10),
            justify="center",
        ).pack(pady=(0, 22))

        self.name_entry = self._entry("Your name:")
        self.days_entry = self._entry("Number of days:")

        btns = tk.Frame(self.window, bg=COLORS["bg"])
        btns.pack(pady=18)

        self._dialog_button(btns, "Confirm", self._confirm, COLORS["green"]).pack(
            side="left", padx=6
        )
        self._dialog_button(btns, "Cancel", self.window.destroy, COLORS["red"]).pack(
            side="left", padx=6
        )

        self.name_entry.focus_set()
        self.window.bind("<Return>", lambda _e: self._confirm())
        self.window.bind("<Escape>", lambda _e: self.window.destroy())

    def _entry(self, label):
        tk.Label(
            self.window,
            text=label,
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=44)

        entry = tk.Entry(
            self.window,
            font=("Segoe UI", 11),
            bg=COLORS["surface"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            bd=8,
            highlightthickness=1,
            highlightbackground=COLORS["overlay"],
            highlightcolor=COLORS["blue"],
        )
        entry.pack(fill="x", padx=44, pady=(3, 12))
        return entry

    def _dialog_button(self, parent, text, command, color):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=COLORS["bg"],
            activebackground=color,
            activeforeground=COLORS["bg"],
            font=("Segoe UI", 11, "bold"),
            bd=0,
            relief="flat",
            padx=28,
            pady=9,
            cursor="hand2",
            highlightthickness=0,
        )
        btn.bind("<Enter>", lambda _e: btn.config(bg=COLORS["text"]))
        btn.bind("<Leave>", lambda _e: btn.config(bg=color))
        return btn

    def _confirm(self):
        name = self.name_entry.get().strip()
        days_str = self.days_entry.get().strip()

        if not name:
            messagebox.showerror(
                "Error", "Please enter your name.", parent=self.window
            )
            return

        try:
            days = int(days_str)
            if days <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error",
                "Days must be a positive number.",
                parent=self.window,
            )
            return

        self.window.destroy()
        self.on_confirm(self.car, name, days)


def main():
    root = tk.Tk()
    CarRentalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
