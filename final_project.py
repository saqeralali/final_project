import pickle
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

class Ticket:
    def __init__(self, ticket_id, type, price, validity, features, availability):
        self.ticket_id = ticket_id
        self.type = type
        self.price = price
        self.validity = validity
        self.features = features
        self.availability = availability

    def update_availability(self, quantity):
        self.availability += quantity

class Order:
    def __init__(self, order_id, user_id, ticket, date, payment_method):
        self.order_id = order_id
        self.user_id = user_id
        self.ticket = ticket
        self.date = date
        self.payment_method = payment_method

    def calculate_discount(self, discount_rate=0.9):
        if self.ticket.type == "group":
            return self.ticket.price * discount_rate
        return self.ticket.price

class User:
    def __init__(self, user_id, name, email, password):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.purchase_history = []

    def add_order(self, order):
        self.purchase_history.append(order)

    def view_orders(self):
        return self.purchase_history

    def get_order(self, order_id):
        for order in self.purchase_history:
            if order.order_id == order_id:
                return order
        return None

    def delete_order(self, order_id):
        self.purchase_history = [o for o in self.purchase_history if o.order_id != order_id]

    def update_account_info(self, name=None, email=None, password=None):
        if name:
            self.name = name
        if email:
            self.email = email
        if password:
            self.password = password

class BookingSystem:
    def __init__(self):
        self.users = []
        self.tickets = []
        self.orders = []

    def register_user(self, user):
        self.users.append(user)

    def find_user(self, email, password):
        for user in self.users:
            if user.email == email and user.password == password:
                return user
        return None

    def purchase_ticket(self, user, ticket_id, payment_method):
        ticket = next((t for t in self.tickets if t.ticket_id == ticket_id), None)
        if not ticket or ticket.availability <= 0:
            raise Exception("Ticket not available.")
        order = Order(len(self.orders) + 1, user.user_id, ticket, datetime.now(), payment_method)
        user.add_order(order)
        self.orders.append(order)
        ticket.update_availability(-1)

    def delete_order_from_system(self, user, order_id):
        order = user.get_order(order_id)
        if not order:
            raise Exception("Order not found.")
        order.ticket.update_availability(1)
        user.delete_order(order_id)
        self.orders = [o for o in self.orders if o.order_id != order_id]

    def save_to_file(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load_from_file(filename):
        with open(filename, "rb") as file:
            return pickle.load(file)

class TicketApp:
    def __init__(self, root, system):
        self.system = system
        self.root = root
        self.root.geometry("400x400")
        self.root.title("Grand Prix Ticket Booking System")
        self.current_user = None
        self.init_main_screen()

    def init_main_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Email").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        tk.Label(self.root, text="Password").pack()
        self.pass_entry = tk.Entry(self.root, show="*")
        self.pass_entry.pack()

        tk.Button(self.root, text="Login", command=self.login_user).pack()
        tk.Button(self.root, text="Register", command=self.register_screen).pack()
        tk.Button(self.root, text="Admin Login", command=self.admin_login).pack()

    def register_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Name").pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()

        tk.Label(self.root, text="Email").pack()
        self.reg_email_entry = tk.Entry(self.root)
        self.reg_email_entry.pack()

        tk.Label(self.root, text="Password").pack()
        self.reg_pass_entry = tk.Entry(self.root, show="*")
        self.reg_pass_entry.pack()

        tk.Button(self.root, text="Register", command=self.register_user).pack()
        tk.Button(self.root, text="Back", command=self.init_main_screen).pack()

    def register_user(self):
        name = self.name_entry.get()
        email = self.reg_email_entry.get()
        password = self.reg_pass_entry.get()
        user_id = len(self.system.users) + 1
        user = User(user_id, name, email, password)
        self.system.register_user(user)
        messagebox.showinfo("Success", "User registered!")
        self.init_main_screen()

    def login_user(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        user = self.system.find_user(email, password)
        if user:
            self.current_user = user
            self.user_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials!")

    def user_dashboard(self):
        self.clear_screen()
        tk.Label(self.root, text=f"Welcome, {self.current_user.name}!").pack()
        tk.Button(self.root, text="View Available Tickets", command=self.display_tickets).pack()
        tk.Button(self.root, text="Purchase Ticket", command=self.purchase_ticket_ui).pack()
        tk.Button(self.root, text="View My Orders", command=self.view_my_orders).pack()
        tk.Button(self.root, text="Delete My Order", command=self.delete_order_ui).pack()
        tk.Button(self.root, text="Edit My Account", command=self.edit_account_ui).pack()
        tk.Button(self.root, text="Logout", command=self.init_main_screen).pack()

    def display_tickets(self):
        ticket_info = ""
        for ticket in self.system.tickets:
            ticket_info += f"ID: {ticket.ticket_id}, Type: {ticket.type}, Price: {ticket.price}, Available: {ticket.availability}\n"
        messagebox.showinfo("Available Tickets", ticket_info if ticket_info else "No tickets available.")

    def purchase_ticket_ui(self):
        ticket_id = simpledialog.askinteger("Purchase Ticket", "Enter Ticket ID:")
        payment_method = simpledialog.askstring("Payment Method", "Enter Payment Method (credit/debit/wallet):")
        try:
            self.system.purchase_ticket(self.current_user, ticket_id, payment_method)
            messagebox.showinfo("Success", "Ticket purchased!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_my_orders(self):
        order_info = ""
        for order in self.current_user.view_orders():
            order_info += f"Order ID: {order.order_id}, Ticket: {order.ticket.type}, Date: {order.date.strftime('%Y-%m-%d')}, Payment: {order.payment_method}\n"
        messagebox.showinfo("My Orders", order_info if order_info else "No orders found.")

    def delete_order_ui(self):
        if not self.current_user.view_orders():
            messagebox.showinfo("No Orders", "You have no orders to delete.")
            return
        order_id = simpledialog.askinteger("Delete Order", "Enter Order ID to delete:")
        if order_id:
            try:
                self.system.delete_order_from_system(self.current_user, order_id)
                messagebox.showinfo("Success", f"Order {order_id} deleted and ticket availability restored.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def edit_account_ui(self):
        new_name = simpledialog.askstring("Edit Account", "Enter new name (or leave blank):")
        new_email = simpledialog.askstring("Edit Account", "Enter new email (or leave blank):")
        new_password = simpledialog.askstring("Edit Account", "Enter new password (or leave blank):")
        self.current_user.update_account_info(name=new_name, email=new_email, password=new_password)
        messagebox.showinfo("Success", "Account information updated!")

    def admin_login(self):
        password = simpledialog.askstring("Admin Login", "Enter admin password:", show="*")
        if password == "admin123":
            AdminDashboard(self.root, self.system)
        else:
            messagebox.showerror("Access Denied", "Incorrect admin password.")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

class AdminDashboard:
    def __init__(self, root, system):
        self.root = root
        self.system = system
        self.discount_rate = 0.9
        self.build_dashboard()

    def build_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Admin Dashboard").pack()
        tk.Button(self.root, text="View Ticket Sales Per Day", command=self.show_sales_per_day).pack()
        tk.Button(self.root, text="Modify Group Discount", command=self.modify_discount).pack()
        tk.Button(self.root, text="Back to Main Screen", command=self.back_to_main).pack()

    def show_sales_per_day(self):
        sales = {}
        for order in self.system.orders:
            day = order.date.strftime("%Y-%m-%d")
            sales[day] = sales.get(day, 0) + 1
        msg = "\n".join([f"{day}: {count} tickets sold" for day, count in sales.items()])
        messagebox.showinfo("Sales Per Day", msg if msg else "No sales yet.")

    def modify_discount(self):
        new_rate = simpledialog.askfloat("Modify Discount", "Enter new discount rate (e.g., 0.85 for 15% off):")
        if new_rate and 0 < new_rate < 1:
            self.discount_rate = new_rate
            messagebox.showinfo("Success", f"Discount updated to {int((1 - new_rate) * 100)}%")
        else:
            messagebox.showerror("Error", "Invalid discount rate entered.")

    def back_to_main(self):
        self.root.destroy()
        main()

def initialize_system():
    system = BookingSystem()
    system.tickets.append(Ticket(1, "single", 200.0, "1 Day", "Race access", 50))
    system.tickets.append(Ticket(2, "weekend", 500.0, "3 Days", "Full weekend", 30))
    system.tickets.append(Ticket(3, "group", 180.0, "1 Day", "Group discount", 100))
    return system

def main():
    try:
        system = initialize_system()
        root = tk.Tk()
        app = TicketApp(root, system)
        root.mainloop()
        system.save_to_file("system_data.pkl")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()