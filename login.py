import sqlite3
from tkinter import *
import tkinter.messagebox
from tkinter import ttk, messagebox
import random
import time
import datetime

def main():
    root = Tk()
    app = login(root)
    root.mainloop()

class login():
    def __init__(self, master):
        self.master=master
        self.master.title("Login")
        self.master.geometry("800x600+0+0")
        self.master.resizable(False,False)
        self.master.config(bg='powder blue')
        self.frame = Frame(self.master,bg='powder blue')
        self.frame.pack()

        Frame_login = Frame(self.master, bg="white")
        Frame_login.place(x=200, y=100, width=400,height =400)

        title = Label(Frame_login, text="Login", font=("Impact",22,"bold"), bg="white").place(x=10,y=20)

        #username
        lbl_username = Label(Frame_login, text="Username", font=("Roboto", 14,"bold"), bg="white").place(x=10,y=80)
        self.username = Entry(Frame_login, font=("Roboto",14), bg="#E7E6E6")
        self.username.place(x=10,y=120)

        lbl_password = Label(Frame_login, text="Password", font=("Roboto",14,"bold"),bg="white").place(x=10,y=170)
        self.password = Entry(Frame_login, font=("Roboto",14), bg="#E7E6E6")
        self.password.place(x=10,y=220)

        #Button
        btn_login = Button(Frame_login, text="Login",font=("Roboto",12), fg="#6162FF",bg="white", command=self.login).place(x=20,y=270)
        btn_register = Button(Frame_login, text="Register", font=("Roboto",12), fg="#6162FF", bg="white", command=self.new_window).place(x=100,y=270)

    def new_window(self):
        self.new_window=Toplevel(self.master)
        self.app=register(self.new_window)

    def login(self):
        db=sqlite3.connect('id.db')
        db.execute("CREATE TABLE IF NOT EXISTS id(username TEXT, password TEXT)")
        cursor=db.cursor()
        cursor.execute("SELECT * FROM id where username=? AND password=?",(self.username.get(),self.password.get()))
        row=cursor.fetchall()
        if row:
            messagebox.showinfo('info',"Login successful")
        else:
            messagebox.showinfo('info',"Login failed")

class register():
    def __init__(self,master):
        self.master=master
        self.master.title("Register")
        self.master.geometry("800x600+0+0")
        self.master.config(bg="powder blue")
        self.frame=Frame(self.master,bg="powder blue")
        self.frame.pack()

        Frame_login = Frame(self.master, bg="white")
        Frame_login.place(x=200, y=100, width=400, height=400)

        title = Label(Frame_login, text="Register", font=("Impact", 22, "bold"), bg="white").place(x=10, y=20)

        # username
        lbl_username = Label(Frame_login, text="Username", font=("Roboto", 14, "bold"), bg="white").place(x=10, y=80)
        self.username = Entry(Frame_login, font=("Roboto", 14), bg="#E7E6E6")
        self.username.place(x=10, y=120)

        lbl_password = Label(Frame_login, text="Password", font=("Roboto", 14, "bold"), bg="white").place(x=10, y=170)
        self.password = Entry(Frame_login, font=("Roboto", 14), bg="#E7E6E6")
        self.password.place(x=10, y=220)

        # Button
        btn_register = Button(Frame_login, text="Register", font=("Roboto", 12), fg="#6162FF", bg="white", command=self.register).place(x=20, y=270)
        btn_back = Button(Frame_login, text="Back", font=("Roboto", 12), fg="#6162FF", bg="white", command=self.back).place(x=100, y=270)

    def register(self):
        uname=self.username.get()
        pword=self.password.get()
        db = sqlite3.connect('id.db')
        db.execute("CREATE TABLE IF NOT EXISTS id(username TEXT, password TEXT)")
        cursor = db.cursor()
        cursor.execute("INSERT INTO id(username, password) VALUES (?,?)",(uname,pword))
        db.commit()
    def back(self):
        self.master.destroy()

if __name__ == '__main__':
    main()
