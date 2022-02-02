import re
from tkinter import *
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
import threading
import time
import sqlite3
from tkinter import simpledialog
from functools import partial
from PyDictionary import PyDictionary
from PIL import Image, ImageTk
import sys
import os
import shutil


# import requests


def main():
    class Task:
        def __init__(self, name, time, order, completed, duration):
            self.name = name
            self.time = time
            self.order = order
            self.completed = completed
            self.duration = duration

        def altComplete(self):
            self.completed = not self.completed

    window = Tk()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.title("Narrator")
    app_width = 680
    app_height = 680
    x = (screen_width / 2) - (app_width / 2)
    y = (screen_height / 2) - (app_height / 2)
    window.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

    def resource_path0(relative_path):

        base_path = getattr(
            sys,
            '_MEIPASS',
            os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    canvas = Canvas(window, width=680, height=680)
    canvas.pack()
    path = resource_path0("Narrator.png")
    img = ImageTk.PhotoImage(Image.open(path))
    canvas.create_image(0, 0, anchor=NW, image=img)

    tasks = []
    global completedTasks
    completedTasks = []

    def scheduleScreen():

        app_width = int(screen_width / 2)
        app_height = int(screen_height * 0.95)
        x = (screen_width / 2) - (app_width / 2)
        y = (screen_height / 2) - (app_height / 2)
        window.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

        for widget in window.winfo_children():
            widget.destroy()

        dictionary = PyDictionary
        now = datetime.now()
        with sqlite3.connect("Scheduler.db") as db:
            cursor = db.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities(
        id INTEGER PRIMARY KEY,
        activity TEXT NOT NULL,
        timeA INTEGER NOT NULL,
        listPos INTEGER NOT NULL);
        """)

        global pattern
        pattern = r'[^A-Za-z0-9]+'

        cursor.execute("SELECT * FROM activities")
        arrayF = cursor.fetchall()
        orderA = 1
        bigNum = 1

        for z in range(0, len(arrayF)):
            if arrayF[z][3] > bigNum:
                bigNum = arrayF[z][3]

        while True:
            for yVar in range(0, len(arrayF)):
                for item in range(0, len(arrayF)):
                    if arrayF[item][3] == orderA:
                        orderA += 1
                        newTask = Task(arrayF[item][1], arrayF[item][2], arrayF[item][3], False, 0)
                        tasks.append(newTask)

                    else:
                        pass
            if orderA == bigNum + 1:
                break
            else:
                orderA += 1
        global start_background
        start_background = True
        global counterA
        counterA = len(tasks)

        app_width = int(screen_width / 2)
        app_height = int(screen_height * 0.95)
        x = (screen_width / 2) - (app_width / 2)
        y = (screen_height / 2) - (app_height / 2)
        window.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
        window.title("Create Habits")

        topframe = Frame(window)
        topframe.pack(anchor=CENTER)

        lblDate = Label(topframe, text="Schedule for: " + now.strftime("%d-%B-%Y"), font=("Arial", 14))
        lblDate.pack()

        lblDay = Label(topframe, text=now.strftime("%A"), font=("Arial", 20))
        lblDay.pack()

        lblTime = Label(topframe, text=now.strftime("%H:%M:%S"))
        lblTime.pack()

        def background():
            while True:
                backgroundTime = datetime.now()
                if not start_background:
                    window.destroy()
                timeN = backgroundTime.strftime("%H:%M:%S")
                lblTime.config(text=timeN)
                time.sleep(1)

        if start_background:
            b = threading.Thread(name='background', target=background, daemon=True)
            b.start()

        lblAct = Label(topframe, text="", font=("Arial", 28))
        lblAct.pack(pady=15)

        lblTimeA = Label(topframe, text="", font=("Arial", 20))
        lblTimeA.pack(pady=10)

        global checkinB
        checkinB = IntVar()
        checkinB.set(1)
        tskComp = Checkbutton(window, text="Task completed", variable=checkinB)
        tskComp.pack(in_=topframe, pady=5)
        tskComp.lower(topframe)
        global task_start
        task_start = 0

        def next():
            if butNext.cget("text") == "Start your schedule" and len(tasks) < 1:
                butNext.lower(topframe)
                lblAct.config(text="Please schedule your day first.")
                return

            if butNext.cget("text") == "Save Diary":
                messagebox.showwarning("Unsaved diary", "Please save your diary first.")
                diaryMorningScreen()
                return

            try:
                if len(tasks) == counterA:
                    diaryMorningScreen()
                    lblAct.config(text="Complete morning diary entry", )
                    butNext.config(text=f"Save Diary")
                    return
                task_fin = datetime.now()

                tskComp.lift()
                global task_start

                if task_start == 0:
                    task_start = datetime.now()
                else:
                    difference = task_fin - task_start
                    total_minutes = difference.total_seconds()
                    duration = int(total_minutes)
                    task_start = datetime.now()
                    global currTask

                    completedTasks.append(currTask)

                    currTask.duration = int(duration / 60)

                    if (checkinB.get() == 1):
                        currTask.completed = True

                currTask = tasks.pop(0)
                activity = currTask.name
                lblAct.config(text=activity)
                lblAct.pack()

                aTime = currTask.time
                alarm_time = datetime.now() + timedelta(minutes=aTime)
                alarm_time = alarm_time.strftime("%H:%M:%S")
                lblTimeA.config(text=f"Aim to complete by: {alarm_time}")
                butNext.config(text=f"Next task")

            except Exception as e:
                diaryScreen()
                lblAct.config(text="Good work, tasks completed." + "\n" + "Please update your schedule for tomorrow." +
                                   "\n" + "Stay Hard!", font=("Arial", 14))
                alarm_time = datetime.now()
                alarm_time = alarm_time.strftime("%H:%M:%S")
                lblTimeA.config(text=f"You completed your schedule at: {alarm_time}")
                butNext.lower(topframe)
                tskComp.lower(topframe)
                butSched.config(text="Save Diary", font=("Arial", 20))
                pass

            '''if activity == "Breathing":
                global driver
                driver = webdriver.Chrome(service=s)
                driver.get("https://www.youtube.com/watch?v=tybOi4hjZFQ")
            if activity == "Work for an hour":
                driver.quit()
                pass
            '''

        def doneScreen(screen):

            cursor.execute("SELECT * FROM activities")
            arrayF = cursor.fetchall()

            orderA = 1
            bigNum = 1

            for z in range(0, len(arrayF)):
                if arrayF[z][3] > bigNum:
                    bigNum = arrayF[z][3]

            while True:
                for yVar in range(0, len(arrayF)):
                    for item in range(0, len(arrayF)):
                        if arrayF[item][3] == orderA:
                            orderA += 1
                            newTask = Task(arrayF[item][1], arrayF[item][2], arrayF[item][3], False, 0)
                            tasks.append(newTask)
                        else:
                            pass
                if orderA == bigNum + 1:
                    break
                else:
                    orderA += 1
            global counterA
            counterA = len(tasks)

            screen.destroy()

            lblAct.config(text="")

            lblTimeA.config(text="")
            butNext.lift(topframe)
            butNext.config(text="Start your schedule")
            butSched.config(text="Schedule your day", font=("Helvetica", 12))

        butNext = Button(window, text="Start your schedule", command=next, font=("Arial", 20))
        butNext.pack(in_=topframe)

        def modSchedule():
            '''if len(activities) < 1:
                cursor.execute("INSERT INTO activities(activity, timeA, listPos) VALUES (?, ?, ?)",
                               ("Enter a task", 2, 1))'''
            for widget in window.winfo_children():
                if ".!toplevel" in str(widget):
                    exits = True
                    if exits:
                        widget.destroy()
            if butSched.cget("text") == "Save Diary":
                messagebox.showwarning("Unsaved diary", "Please save your diary first.")
                diaryScreen()
                return
            elif butSched.cget("text") == "Save Schedule":
                messagebox.showwarning("Save schedule", "Please save your schedule.")
            else:
                butSched.config(text="Save Schedule")
            try:
                butNext.lower(topframe)
                tskComp.lower(topframe)
            except Exception:
                pass

            def addActivity():
                txtActivity = "Activity:"
                txtTime = "Time(Min) for activity:"
                textOrder = "Order of activity:"

                while True:

                    activity = simpledialog.askstring("Please enter new: ", txtActivity)
                    if activity is None:
                        break
                    if activity == "":
                        messagebox.showwarning("showwarning", "Please enter a valid activity.")
                        continue
                    timeA = simpledialog.askinteger("Please enter new: ", txtTime)
                    if timeA is None:
                        break
                    if timeA < 0 or timeA > 720:
                        messagebox.showwarning("showwarning", "Please enter a valid time(mins) for activity.")
                        continue
                    listPos = simpledialog.askinteger("Please enter new: ", textOrder)
                    if listPos is None:
                        break
                    if listPos < 1 or listPos > 50:
                        messagebox.showwarning("showwarning", "Please enter a valid task order.")
                        continue

                    cursor.execute("SELECT * FROM activities")
                    collision = cursor.fetchall()
                    orderList = []

                    for c in range(0, len(collision)):
                        orderList.append(f"A{str(collision[c][3])}A")

                    matching = [s for s in orderList if f"A{str(listPos)}A" in s]

                    if not matching:
                        insert_fields = """INSERT INTO activities(activity, timeA, listPos)
                                VALUES (?, ?, ?)"""
                        cursor.execute(insert_fields, (activity, timeA, listPos))
                        break

                    messagebox.showwarning("showwarning", "Task order already in use.\nPlease update your order first.")
                    continue

                db.commit()
                gridSched()

                # activities.append(txtN.get())
                # minutes.append(30)

            def removeEntry(input):
                cursor.execute('SELECT activity FROM activities WHERE id = ?', (input,))
                activity = str(cursor.fetchall())

                # Remove special characters from the string
                act = re.sub(pattern, ' ', activity)

                if messagebox.askyesno("Deleting Entry", f"Are you sure you want to delete task: {act}"):
                    sql = "DELETE FROM activities WHERE id = ?"

                    cursor.execute(sql, (input,))

                    db.commit()
                    gridSched()

            def updateEntry(input):

                actV = "Activity"
                timeV = "Time(Min) for activity"
                rowV = "Order of activity"

                while True:
                    activity = simpledialog.askstring("Please enter new: ", actV)
                    if activity is None:
                        break
                    if activity == "":
                        messagebox.showwarning("showwarning", "Please enter a valid activity.")
                        continue
                    timeA = simpledialog.askinteger("Please enter new: ", timeV)
                    if timeA is None:
                        break
                    if timeA < 0 or timeA > 720:
                        messagebox.showwarning("showwarning", "Please enter a valid time(mins) for activity.")
                        continue
                    listPos = simpledialog.askinteger("Please enter new: ", rowV)
                    if listPos is None:
                        break
                    if listPos < 1 or listPos > 50:
                        messagebox.showwarning("showwarning", "Please enter a valid task order.")
                        continue

                    sql = "UPDATE activities SET activity =?, timeA =?, listPos = ? WHERE id = ?"

                    cursor.execute(sql, (activity, timeA, listPos, input,))
                    break

                db.commit()
                gridSched()

            modSchedScreen = Toplevel(window)

            app_width = int(screen_width / 2)
            app_height = int(screen_height)
            x = (screen_width / 2) - (app_width / 2)
            y = (screen_height / 2) - (app_height / 2)
            modSchedScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
            modSchedScreen.title("Add new habits")

            def gridSched():
                global completedTasks
                completedTasks = []
                global task_start
                task_start = 0
                for widget in modSchedScreen.winfo_children():
                    widget.destroy()
                btn = Button(modSchedScreen, text="Add new activity +", command=addActivity)
                btn.grid(column=1, row=1, pady=10)

                btn = Button(modSchedScreen, text="Save", command=partial(doneScreen, modSchedScreen))
                btn.grid(column=4, row=1)

                lbl = Label(modSchedScreen, text="Order")
                lbl.grid(column=0, row=2, padx=30)

                lbl = Label(modSchedScreen, text="Activity")
                lbl.grid(column=1, row=2, padx=80)

                lbl = Label(modSchedScreen, text="Time(Min)")
                lbl.grid(column=2, row=2, padx=40)

                cursor.execute("SELECT * FROM activities")
                if cursor.fetchall() is not None:
                    x = 0
                    iFont = 13
                    while True:

                        cursor.execute("SELECT * FROM activities")
                        array = cursor.fetchall()
                        global arrayNew
                        arrayNew = []
                        listP = 1
                        bigNum = 1

                        for z in range(0, len(array)):
                            if array[z][3] > bigNum:
                                bigNum = array[z][3]

                        while True:
                            for yV in range(0, len(array)):
                                for i in range(0, len(array)):
                                    if array[i][3] == listP:
                                        arrayNew.append(array[i])
                                        listP += 1
                            if listP == bigNum + 1:
                                break
                            else:
                                listP += 1

                        if (len(array) == 0):
                            break

                        if x > 11:
                            for widget in modSchedScreen.winfo_children():
                                widget.config(font=("Arial", iFont))
                            iFont -= 1

                        lblOne = Label(modSchedScreen, text=arrayNew[x][3], font=("Arial", 14))
                        lblOne.grid(column=0, row=x + 3)

                        lblOne = Label(modSchedScreen, text=arrayNew[x][1])
                        lblOne.grid(column=1, row=x + 3)

                        lblOne = Label(modSchedScreen, text=arrayNew[x][2])
                        lblOne.grid(column=2, row=x + 3)

                        btn = Button(modSchedScreen, text="Delete", command=partial(removeEntry, arrayNew[x][0]),
                                     font=("Arial", 14))
                        btn.grid(column=3, row=x + 3, pady=10, padx=10)

                        btn = Button(modSchedScreen, text="Update", command=partial(updateEntry, arrayNew[x][0]))
                        btn.grid(column=4, row=x + 3, pady=10)

                        x += 1

                        cursor.execute("SELECT * FROM activities")
                        if len(arrayNew) <= x:
                            break

            gridSched()

        butSched = Button(topframe, text="Schedule your day", font=("Arial", 12), command=modSchedule)
        butSched.pack(pady=50)

        def bookScreen():
            for widget in window.winfo_children():
                if ".!toplevel" in str(widget):
                    exits = True
                    if exits:
                        widget.destroy()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Books(
            id INTEGER PRIMARY KEY,
            book TEXT NOT NULL,
            chapter INTEGER,
            summary TEXT,
            vocabulary TEXT);
            """)

            def addBook():
                while True:
                    newBookName = simpledialog.askstring("Book name: ", "Please enter book name: ")

                    if newBookName is None:
                        break
                    if newBookName == "":
                        messagebox.showwarning("showwarning", "Please enter a valid book name.")
                        continue

                    newChapters = simpledialog.askinteger("Chapter amount: ",
                                                          "Please enter the amount of chapters in the book: ")

                    if newChapters is None:
                        break

                    if 50 < newChapters or newChapters < 1:
                        messagebox.showwarning("showwarning", "Please enter a valid chapter amount.")
                        continue
                    summaryB = ""
                    for i in range(1, newChapters + 1):
                        summaryB += f"\nChapter {i}:\n\n================\n"

                    bookSummary.insert(1.0, summaryB)
                    cursor.execute("INSERT INTO Books(book, chapter, summary, vocabulary) VALUES (?, ?, ?, ?)",
                                   (newBookName, newChapters, summaryB, ""))
                    db.commit()
                    cursor.execute('SELECT id FROM books ORDER BY id DESC LIMIT 1')
                    choice = cursor.fetchall()

                    cursor.execute('SELECT * FROM books WHERE id = ?', (choice[0]))
                    activity = cursor.fetchall()

                    bookName.delete(0, "end")
                    bookName.insert(0, activity[0][1])
                    bookChapter.delete(0, "end")
                    bookChapter.insert(0, activity[0][2])
                    bookSummary.delete(1.0, "end")
                    bookSummary.insert(1.0, activity[0][3])
                    bookVocabulary.delete(1.0, "end")
                    bookVocabulary.insert(1.0, activity[0][4])

                    global currentSel
                    currentSel = activity
                    butSave.config(command=partial(updateBook, currentSel))
                    butAddVoc.config(command=addVocab)
                    break

            def selectBook():
                cursor.execute('SELECT id, book FROM Books')
                booksArr = cursor.fetchall()
                if booksArr == []:
                    messagebox.showwarning("No book", "Please add a new book first.")
                    return

                for widget in bookWindow.winfo_children():
                    if ".!toplevel.!toplevel" in str(widget):
                        exists = True
                        if exists:
                            widget.destroy()

                selectBScreen = Toplevel(bookWindow)
                selectBScreen.title("Select Book")
                app_width = 300
                app_height = 300
                x = (screen_width / 2) - (app_width / 2)
                y = (screen_height / 2) - (app_height / 2)
                selectBScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

                books = []
                bookIdList = []
                for i in range(0, len(booksArr)):
                    book = re.sub(pattern, ' ', str(booksArr[i][1]))
                    bookIdList.append(booksArr[i][0])
                    books.append(book)
                scrollBar = Scrollbar(selectBScreen, bg="grey")

                scrollBar.pack(side=RIGHT, fill=BOTH)
                bookList = Listbox(selectBScreen, selectmode=BROWSE, yscrollcommand=scrollBar.set)
                scrollBar.config(command=bookList.yview)
                bookList.pack(fill=BOTH, pady=10, padx=10)

                for i in range(0, len(books)):
                    bookList.insert(i, books[i])

                def selectedBook():
                    while True:
                        if bookList.curselection() == ():
                            break
                        choice = re.sub(pattern, ' ', str(bookList.curselection()))
                        choice = bookIdList[int(choice)]
                        if choice == ():
                            messagebox.showwarning("showwarning", "Please select a book.")
                            break
                        cursor.execute('SELECT * FROM books WHERE id = ?', (choice,))
                        activity = cursor.fetchall()

                        bookName.delete(0, "end")
                        bookName.insert(0, activity[0][1])
                        bookChapter.delete(0, "end")
                        bookChapter.insert(0, activity[0][2])

                        bookSummary.delete(1.0, "end")
                        if activity[0][3] != "":
                            bookSummary.insert(1.0, activity[0][3])
                        bookVocabulary.delete(1.0, "end")
                        if activity[0][4] != "":
                            bookVocabulary.insert(1.0, activity[0][4])

                        global currentSel
                        currentSel = activity
                        butSave.config(command=partial(updateBook, currentSel))
                        butAddVoc.config(command=addVocab)
                        selectBScreen.destroy()
                        break

                butOk = Button(selectBScreen, text="Select", command=selectedBook)
                butOk.pack()

                def removeBook():
                    while True:
                        if bookList.curselection() == ():
                            break

                        choice = re.sub(pattern, '', str(bookList.curselection()))
                        choice = bookIdList[int(choice)]
                        if choice == ():
                            messagebox.showwarning("showwarning", "Please select a book.")
                            break
                        cursor.execute('SELECT book FROM Books WHERE id = ?', (choice,))
                        book = str(cursor.fetchall())
                        # Remove special characters from the string
                        bookS = re.sub(pattern, ' ', book)

                        if messagebox.askyesno("Deleting Entry", f"Are you sure you want to delete book: {bookS}"):
                            sql = "DELETE FROM Books WHERE id = ?"

                            cursor.execute(sql, (choice,))
                            db.commit()

                            bookList.delete(choice)
                            selectBScreen.destroy()
                            bookName.delete(0, "end")
                            bookChapter.delete(0, "end")
                            bookSummary.delete(1.0, "end")
                            bookVocabulary.delete(1.0, "end")
                            butSave.config(command=notify)
                            butAddVoc.config(command=notify)
                        break

                butDeleteBook = Button(selectBScreen, text="Delete Book", command=removeBook)
                butDeleteBook.pack()

                def desBookScreen():
                    selectBScreen.destroy()

                butDone = Button(selectBScreen, text="Back", command=desBookScreen)
                butDone.pack(padx=10, pady=5, side=TOP)

            bookWindow = Toplevel(window)
            bookWindow.title("Your Books")
            app_width = int(screen_width / 2)
            app_height = int(screen_height * 0.95)
            x = (screen_width / 2) - (app_width / 2)
            y = (screen_height / 2) - (app_height / 2)
            bookWindow.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
            top = Frame(bookWindow)
            top.pack()

            middle = Frame(bookWindow, width=500, height=100)
            middle.pack()

            bottom = Frame(bookWindow, width=500, height=100)
            bottom.pack()

            addBook = Button(bookWindow, text="Add new book", command=addBook)
            addBook.pack(in_=top, side=TOP, pady=5)

            selectBook = Button(bookWindow, text="Select book", command=selectBook)
            selectBook.pack(in_=top, side=TOP, pady=5)

            lblName = Label(bookWindow, text="Name: ")
            lblName.pack(in_=top, side=LEFT, padx=5, pady=5)

            bookName = Entry(bookWindow)
            bookName.pack(in_=top, side=LEFT)

            lblChapter = Label(bookWindow, text="Chapters: ")
            lblChapter.pack(in_=top, side=LEFT, padx=5, pady=5)

            bookChapter = Entry(bookWindow)
            bookChapter.pack(in_=top, side=LEFT)

            lblSummary = Label(middle, text="Summary: ")
            lblSummary.pack(in_=middle)

            bookSummary = Text(bookWindow, wrap=WORD, height=20, undo=TRUE)
            bookSummary.pack(in_=middle, pady=5, padx=10, expand=TRUE, fill=BOTH)

            lblVocabulary = Label(bookWindow, text="Vocabulary: ")
            lblVocabulary.pack(in_=bottom, side=TOP)

            def notify():
                messagebox.showwarning("Select book", "Please select or add a book first.")
                bookName.delete(0, "end")
                bookChapter.delete(0, "end")
                bookSummary.delete(1.0, "end")
                bookVocabulary.delete(1.0, "end")

            butAddVoc = Button(bookWindow, text="Add to Vocabulary", command=notify)
            butAddVoc.pack(in_=bottom, padx=10, pady=5, side=TOP)

            bookVocabulary = Text(bookWindow, wrap=WORD, height=10, undo=TRUE)
            bookVocabulary.pack(in_=bottom, expand=TRUE, fill=BOTH, pady=5, padx=10)

            def updateBook(currentSel):
                while True:
                    id = currentSel[0][0]
                    book = bookName.get()
                    chapter = bookChapter.get()
                    summaryB = bookSummary.get("1.0", 'end-1c')

                    vocabulary = bookVocabulary.get("1.0", 'end-1c')
                    if book == "":
                        messagebox.showwarning("showwarning", "Please enter a valid book name.")
                        break
                    if chapter == "" or 50 < int(chapter) < 1:
                        messagebox.showwarning("showwarning", "Please enter a valid chapter.")
                        break

                    bookSummary.delete(1.0, 'end')
                    for i in range(1, int(chapter) + 1):
                        if f"Chapter {i}:" not in summaryB:
                            summaryB = f"{summaryB}\nChapter {i}:\n\n================\n"

                    bookSummary.insert(1.0, summaryB)
                    sql = "UPDATE Books SET book =?, chapter =?, summary = ?, vocabulary = ? WHERE id = ?"

                    cursor.execute(sql, (book, chapter, summaryB, vocabulary, id,))
                    db.commit()
                    messagebox.showinfo("Success", f"Book: {book} was successfully updated!")
                    break

            butSave = Button(bookWindow, text="Save", command=notify)
            butSave.pack(padx=10, pady=5, side=TOP)

            def addVocab():
                for widget in bookWindow.winfo_children():
                    if ".!toplevel.!toplevel" in str(widget):
                        exists = True
                        if exists:
                            widget.destroy()

                addVocabScreen = Toplevel(bookWindow)
                addVocabScreen.title("Add a word to your vocabulary")
                app_width = 300
                app_height = 300
                x = (screen_width / 2) - (app_width / 2)
                y = (screen_height / 2) - (app_height / 2)
                addVocabScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

                lblWord = Label(addVocabScreen, text="Add a word to your vocabulary:")
                lblWord.pack(padx=10, pady=5, side=TOP)

                entWord = Entry(addVocabScreen)
                entWord.pack(padx=10, pady=5, side=TOP)

                def addWord():
                    enteredWord = entWord.get()
                    butAdd.config(text="Finding word", state=DISABLED)
                    if enteredWord == "":
                        messagebox.showinfo("No match", "Please enter a word into the text field.")
                    elif " " in enteredWord:
                        messagebox.showinfo("Multiple words", "Please enter a single word into the text field.")
                    else:
                        while True:
                            meaning = ""
                            try:
                                meaning += f"Noun : {dictionary.meaning(enteredWord, disable_errors=True)['Noun'][0]} \n"
                            except Exception:
                                pass
                            try:
                                meaning += f"Verb : {dictionary.meaning(enteredWord, disable_errors=True)['Verb'][0]} \n"
                            except Exception:
                                pass
                            try:
                                meaning += f"Adjective : {dictionary.meaning(enteredWord, disable_errors=True)['Adjective'][0]} \n"
                            except Exception:
                                try:
                                    meaning += f"Adverb : {dictionary.meaning(enteredWord, disable_errors=True)['Adverb'][0]} \n"
                                except Exception:
                                    try:
                                        meaning += f"Pronoun : {dictionary.meaning(enteredWord, disable_errors=True)['Pronoun'][0]} \n"
                                    except Exception:
                                        try:
                                            meaning += f"Preposition : {dictionary.meaning(enteredWord, disable_errors=True)['Preposition'][0]} \n"
                                        except Exception:
                                            try:
                                                meaning += f"Conjunction : {dictionary.meaning(enteredWord, disable_errors=True)['Conjunction'][0]} \n"
                                            except Exception:
                                                try:
                                                    meaning += f"Interjection : {dictionary.meaning(enteredWord, disable_errors=True)['Interjection'][0]} \n"
                                                except Exception:
                                                    pass
                            if meaning == "":
                                messagebox.showinfo("No match", "Definition for entered word can not be found.")
                            else:
                                bookVocabulary.insert(1.0, f"{enteredWord} - {meaning}\n")

                                id = currentSel[0][0]
                                vocabulary = bookVocabulary.get("1.0", 'end-1c')

                                sql = "UPDATE Books SET vocabulary = ? WHERE id = ?"

                                cursor.execute(sql, (vocabulary, id,))
                                db.commit()
                            break
                    entWord.delete(0, 'end')
                    butAdd.config(text="Search word", state=NORMAL)

                butAdd = Button(addVocabScreen, text="Search Word", command=addWord)
                butAdd.pack(padx=10, pady=5, side=TOP)

                def desVoc():
                    addVocabScreen.destroy()

                butDone = Button(addVocabScreen, text="Back", command=desVoc)
                butDone.pack(padx=10, pady=5, side=TOP)

            def vocabScreen():
                for widget in bookWindow.winfo_children():
                    if ".!toplevel.!toplevel" in str(widget):
                        exists = True
                        if exists:
                            widget.destroy()
                vocScreen = Toplevel(bookWindow)
                vocScreen.title("List of words in vocabulary")
                app_width = 500
                app_height = 500
                x = (screen_width / 2) - (app_width / 2)
                y = (screen_height / 2) - (app_height / 2)
                vocScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

                cursor.execute('SELECT vocabulary FROM books')
                vocabularyArr = cursor.fetchall()

                vocabTxt = Text(vocScreen, wrap=WORD, height=20, undo=TRUE)
                vocabTxt.pack(pady=5, padx=10, expand=TRUE, fill=BOTH)

                vocabTxt.delete(1.0, "end")

                for i in range(0, len(vocabularyArr)):
                    strWord = str(vocabularyArr[i][0])

                    vocabTxt.insert(1.0, f"{strWord}")

                if vocabTxt.get(1.0, "end-1c") == "":
                    messagebox.showwarning("Empty vocabulary",
                                           "Your vocabulary is empty!\nAdd a word by clicking the Add to Vocabulary button.")
                    vocScreen.destroy()
                    return

            butBook = Button(bookWindow, text="Your Vocabulary", font=("Helvetica", 14), command=vocabScreen)
            butBook.pack(side=TOP)

            def doneCom():
                option = messagebox.askyesno("Quit",
                                             "Are you sure you want to return to the main screen? \n \n Unsaved changes will be lost.")
                if option:
                    bookWindow.destroy()

            butDone = Button(bookWindow, text="Back", font=("Helvetica", 14), command=doneCom)
            butDone.pack(side=TOP, padx=10, pady=10)

            bookWindow.protocol("WM_DELETE_WINDOW", partial(on_closing, bookWindow))

        butBook = Button(topframe, text="Books", font=("Arial", 10), command=bookScreen)
        butBook.pack()

        def diaryMorningScreen():
            for widget in window.winfo_children():
                if ".!toplevel" in str(widget):
                    exits = True
                    if exits:
                        widget.destroy()
            global currentDSel

            diaryWindow = Toplevel(window)
            diaryWindow.title("'"'Fail to plan, plan to fail.'"'")
            app_width = 700
            app_height = 400
            x = (screen_width / 2) - (app_width / 2)
            y = (screen_height / 2) - (app_height / 2)
            diaryWindow.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
            top = Frame(diaryWindow)
            top.pack()

            lblDay = Label(diaryWindow, text="Diary entry for: " + now.strftime("%A"), font=("Arial", 14))
            lblDay.pack(in_=top, side=TOP, pady=5)

            lblDate = Label(diaryWindow, text=now.strftime("%d-%B-%Y"), font=("Arial", 20))
            lblDate.pack(in_=top, side=TOP, pady=5)

            lblGrateful = Label(diaryWindow, text="I am grateful for: ")
            lblGrateful.pack(in_=top, side=TOP, padx=5, pady=5)

            gratefulTxt = Text(diaryWindow, wrap=WORD, height=3, undo=TRUE)
            gratefulTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

            lblPlan = Label(diaryWindow, text="This is how I will make today great: ")
            lblPlan.pack(in_=top, side=TOP, padx=5, pady=5)

            planTxt = Text(diaryWindow, wrap=WORD, height=5, undo=TRUE)
            planTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

            lblAffirmation = Label(diaryWindow, text="Positive affirmation: ")
            lblAffirmation.pack(in_=top, side=TOP, padx=5, pady=5)

            affirmationTxt = Text(diaryWindow, wrap=WORD, height=2, undo=TRUE)
            affirmationTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

            def updateDiary(currentDSel):
                while True:
                    id = currentDSel[0][0]
                    dateD = lblDate.cget("text")
                    grateful = gratefulTxt.get("1.0", 'end-1c')
                    plan = planTxt.get("1.0", 'end-1c')
                    affirmation = affirmationTxt.get("1.0", 'end-1c')

                    sql = "UPDATE Diary SET date =?, grateful =?, plan = ?, affirmation = ? WHERE id = ?"

                    cursor.execute(sql, (dateD, grateful, plan, affirmation, id,))
                    db.commit()
                    messagebox.showinfo("Success", f"Diary: {dateD} was successfully updated!")
                    doneCom()
                    break

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Diary(
            id INTEGER PRIMARY KEY,
            date DATE NOT NULL,
            grateful TEXT,
            plan TEXT,
            affirmation TEXT,
            deed TEXT,
            improvement TEXT,
            experiences TEXT,
            day DATE);
            """)

            cursor.execute('SELECT date FROM Diary ORDER BY id DESC LIMIT 1')
            latestDiary = cursor.fetchall()
            if latestDiary == []:
                cursor.execute(
                    "INSERT INTO Diary(date, grateful, plan, affirmation, deed, improvement, experiences, day) VALUES (?, ?, ?, ?,?,?,?,?)",
                    (now.strftime("%d-%B-%Y"), "1.\n2.\n3.", "", "", "", "", "1.\n2.\n3.", now.strftime("%A")))
                cursor.execute('SELECT * FROM Diary ORDER BY id DESC LIMIT 1')
                diary = cursor.fetchall()

                currentDSel = diary
            elif latestDiary[0][0] != now.strftime("%d-%B-%Y"):
                cursor.execute(
                    "INSERT INTO Diary(date, grateful, plan, affirmation, deed, improvement, experiences, day) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (now.strftime("%d-%B-%Y"), "1.\n2.\n3.", "", "", "", "", "1.\n2.\n3.", now.strftime("%A")))
                cursor.execute('SELECT * FROM Diary ORDER BY id DESC LIMIT 1')
                diary = cursor.fetchall()
                currentDSel = diary
            else:
                cursor.execute('SELECT * FROM Diary ORDER BY id DESC LIMIT 1')
                diary = cursor.fetchall()
                currentDSel = diary

            lblDay.config(text=f"Diary entry for: {diary[0][8]}")
            lblDate.config(text=diary[0][1])

            gratefulTxt.delete(1.0, "end")
            if diary[0][2] != "":
                gratefulTxt.insert(1.0, diary[0][2])
            planTxt.delete(1.0, "end")
            if diary[0][3] != "":
                planTxt.insert(1.0, diary[0][3])
            affirmationTxt.delete(1.0, "end")
            if diary[0][4] != "":
                affirmationTxt.insert(1.0, diary[0][4])

            db.commit()

            butSave = Button(diaryWindow, text="Save", command=partial(updateDiary, currentDSel))
            butSave.pack(padx=10, pady=5, side=TOP)

            def doneCom():
                global counterA
                counterA += 1
                butNext.config(text="Next task")
                option = messagebox.askyesno("Quit", "Do you want to return to the main screen?")
                if option:
                    diaryWindow.destroy()

            diaryWindow.protocol("WM_DELETE_WINDOW", partial(on_closing, diaryWindow))

        def diaryScreen():
            for widget in window.winfo_children():
                if ".!toplevel" in str(widget):
                    exits = True
                    if exits:
                        widget.destroy()
            global currentDSel
            '''def addDiaryEntry():
                while True:
                    newBookName = simpledialog.askstring("Please enter book name: ", "Book name:")
                    if newBookName == None:
                        break
                    if newBookName == "":
                        messagebox.showwarning("showwarning", "Please enter a valid activity")
                        continue
                    cursor.execute("INSERT INTO Books(book, chapter, summary, vocabulary) VALUES (?, ?, ?, ?)",
                                   (newBookName, 1, "Chapter 1:\n\n================", ""))
                    db.commit()
                    cursor.execute('SELECT id FROM books ORDER BY id DESC LIMIT 1')
                    choice = cursor.fetchall()
                    cursor.execute('SELECT * FROM books WHERE id = ?', (choice[0]))
                    activity = cursor.fetchall()
                    bookName.delete(0, "end")
                    bookName.insert(0, activity[0][1])
                    bookChapter.delete(0, "end")
                    bookChapter.insert(0, activity[0][2])
                    bookSummary.delete(1.0, "end")
                    bookSummary.insert(1.0, activity[0][3])
                    bookVocabulary.delete(1.0, "end")
                    bookVocabulary.insert(1.0, activity[0][4])
                    global currentSel
                    currentSel = activity
                    butSave.config(command=partial(updateBook, currentSel))
                    break
            '''

            def selectDiary():
                cursor.execute('SELECT id, date FROM Diary')
                diaryArr = cursor.fetchall()
                if diaryArr == []:
                    notify()
                    return
                for widget in diaryWindow.winfo_children():
                    if ".!toplevel.!toplevel" in str(widget):
                        exists = True
                        if exists:
                            widget.destroy()

                selectDScreen = Toplevel(diaryWindow)
                selectDScreen.title("Select Date of Diary entry")
                app_width = 300
                app_height = 300
                x = (screen_width / 2) - (app_width / 2)
                y = (screen_height / 2) - (app_height / 2)
                selectDScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

                diaries = []
                diaryIdList = []
                for i in range(0, len(diaryArr)):
                    dateD = re.sub(pattern, ' ', str(diaryArr[i][1]))
                    diaryIdList.append(diaryArr[i][0])
                    diaries.append(dateD)
                scrollBar = Scrollbar(selectDScreen, bg="grey")

                scrollBar.pack(side=RIGHT, fill=BOTH)
                diaryList = Listbox(selectDScreen, selectmode=BROWSE, yscrollcommand=scrollBar.set)

                scrollBar.config(command=diaryList.yview)
                diaryList.pack(fill=BOTH, pady=10, padx=10)

                for i in range(0, len(diaries)):
                    diaryList.insert(i, diaries[i])

                def selectedDiary():
                    while True:
                        if diaryList.curselection() == ():
                            break
                        choice = re.sub(pattern, ' ', str(diaryList.curselection()))
                        choice = diaryIdList[int(choice)]
                        if choice == ():
                            messagebox.showwarning("showwarning", "Please select a diary entry.")
                            break
                        cursor.execute('SELECT * FROM Diary WHERE id = ?', (choice,))
                        diary = cursor.fetchall()

                        lblDay.config(text=f"Diary entry for: {diary[0][8]}")
                        lblDate.config(text=diary[0][1])

                        gratefulTxt.delete(1.0, "end")
                        if diary[0][2] != "":
                            gratefulTxt.insert(1.0, diary[0][2])
                        planTxt.delete(1.0, "end")
                        if diary[0][3] != "":
                            planTxt.insert(1.0, diary[0][3])
                        affirmationTxt.delete(1.0, "end")
                        if diary[0][4] != "":
                            affirmationTxt.insert(1.0, diary[0][4])
                        deedTxt.delete(1.0, "end")
                        if diary[0][5] != "":
                            deedTxt.insert(1.0, diary[0][5])
                        improveTxt.delete(1.0, "end")
                        if diary[0][6] != "":
                            improveTxt.insert(1.0, diary[0][6])
                        experiencesTxt.delete(1.0, "end")
                        if diary[0][7] != "":
                            experiencesTxt.insert(1.0, diary[0][7])

                        currentDSel = diary
                        butSave.config(command=partial(updateDiary, currentDSel))
                        selectDScreen.destroy()
                        break

                butOk = Button(selectDScreen, text="Select", command=selectedDiary)
                butOk.pack()

                def removeDiary():
                    while True:
                        if diaryList.curselection() == ():
                            break
                        choice = re.sub(pattern, '', str(diaryList.curselection()))
                        choice = diaryIdList[int(choice)]
                        if choice == ():
                            messagebox.showwarning("showwarning", "Please select a diary entry.")
                            break
                        cursor.execute('SELECT date FROM Diary WHERE id = ?', (choice,))
                        diary = str(cursor.fetchall())
                        diaryS = re.sub(pattern, ' ', diary)

                        if messagebox.askyesno("Deleting Entry", f"Are you sure you want to delete diary: {diaryS}"):
                            sql = "DELETE FROM Diary WHERE id = ?"

                            cursor.execute(sql, (choice,))
                            db.commit()

                            diaryList.delete(choice)
                            selectDScreen.destroy()
                            lblDate.config(text="")
                            lblDay.config(text="")
                            gratefulTxt.delete(1.0, "end")

                            planTxt.delete(1.0, "end")
                            affirmationTxt.delete(1.0, "end")
                            deedTxt.delete(1.0, "end")
                            improveTxt.delete(1.0, "end")
                            experiencesTxt.delete(1.0, "end")
                            butSave.config(command=notifySel)
                        break

                butDeleteDiary = Button(selectDScreen, text="Delete Diary", command=removeDiary)
                butDeleteDiary.pack()

                def desDiaryScreen():
                    selectDScreen.destroy()

                butDone = Button(selectDScreen, text="Back", command=desDiaryScreen)
                butDone.pack(padx=10, pady=5, side=TOP)

            diaryWindow = Toplevel(window)
            diaryWindow.title("'""Accountability is the glue that ties commitment to the result.""'")
            app_width = int(screen_width / 2)
            app_height = int(screen_height * 0.95)
            x = (screen_width / 2) - (app_width / 2)
            y = (screen_height / 2) - (app_height / 2)
            diaryWindow.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
            top = Frame(diaryWindow)
            top.pack()

            lblDay = Label(diaryWindow, text="Diary entry for: " + now.strftime("%A"), font=("Arial", 14))
            lblDay.pack(in_=top, side=TOP, pady=5)

            lblDate = Label(diaryWindow, text=now.strftime("%d-%B-%Y"), font=("Arial", 20))
            lblDate.pack(in_=top, side=TOP, pady=5)

            middle = Frame(diaryWindow, width=500, height=100)
            middle.pack()

            bottom = Frame(diaryWindow, width=500, height=100)
            bottom.pack()

            selectDiary = Button(diaryWindow, text="Select diary entry", command=selectDiary)
            selectDiary.pack(in_=top, side=TOP, pady=5)

            lblGrateful = Label(diaryWindow, text="I am grateful for: ")
            lblGrateful.pack(in_=top, side=TOP, padx=5, pady=5)

            gratefulTxt = Text(diaryWindow, wrap=WORD, height=3, undo=TRUE)
            gratefulTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

            lblPlan = Label(diaryWindow, text="This is how I will make today great: ")
            lblPlan.pack(in_=top, side=TOP, padx=5, pady=5)

            planTxt = Text(diaryWindow, wrap=WORD, height=5, undo=TRUE)
            planTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

            lblAffirmation = Label(diaryWindow, text="Positive affirmation: ")
            lblAffirmation.pack(in_=top, side=TOP, padx=5, pady=5)

            affirmationTxt = Text(diaryWindow, wrap=WORD, height=2, undo=TRUE)
            affirmationTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

            '''response = requests.get("https://www.quotes.rest/qod?language=en")
            json_resp = response.json()
            quote = json_resp["contents"]["quotes"][0]["quote"]
            author = json_resp["contents"]["quotes"][0]["author"]
            print(quote)
            print(author)'''

            lblQuote = Label(diaryWindow, text="This will be a quote")
            lblQuote.pack(in_=middle, side=TOP, padx=5, pady=5)

            lblDeed = Label(diaryWindow, text="My good deed for today: ")
            lblDeed.pack(in_=bottom, side=TOP, padx=5, pady=5)

            deedTxt = Text(diaryWindow, wrap=WORD, height=2, undo=TRUE)
            deedTxt.pack(in_=bottom, pady=5, padx=10, expand=TRUE, fill=BOTH)

            lblImprove = Label(diaryWindow, text="How I'll improve: ")
            lblImprove.pack(in_=bottom, side=TOP, padx=5, pady=5)

            improveTxt = Text(diaryWindow, wrap=WORD, height=2, undo=TRUE)
            improveTxt.pack(in_=bottom, pady=5, padx=10, expand=TRUE, fill=BOTH)

            lblExperiences = Label(diaryWindow, text="Great things I experienced today: ")
            lblExperiences.pack(in_=bottom, side=TOP, padx=5, pady=5)

            experiencesTxt = Text(diaryWindow, wrap=WORD, height=3, undo=TRUE)
            experiencesTxt.pack(in_=bottom, pady=5, padx=10, expand=TRUE, fill=BOTH)

            def notify():
                messagebox.showwarning("No diary", " You diary is empty, a new entry will now be created.")
                diaryWindow.destroy()
                diaryScreen()

            def notifySel():
                messagebox.showwarning("No diary", " Please select a diary entry to save to.")

            def updateDiary(currentDSel):
                while True:
                    id = currentDSel[0][0]
                    dateD = lblDate.cget("text")
                    grateful = gratefulTxt.get("1.0", 'end-1c')
                    plan = planTxt.get("1.0", 'end-1c')
                    affirmation = affirmationTxt.get("1.0", 'end-1c')
                    deed = deedTxt.get("1.0", 'end-1c')
                    improve = improveTxt.get("1.0", 'end-1c')
                    experiences = experiencesTxt.get("1.0", 'end-1c')

                    sql = "UPDATE Diary SET date =?, grateful =?, plan = ?, affirmation = ?, deed = ?, improvement = ?, experiences = ? WHERE id = ?"

                    cursor.execute(sql, (dateD, grateful, plan, affirmation, deed, improve, experiences, id,))
                    db.commit()
                    messagebox.showinfo("Success", f"Diary: {dateD} was successfully updated!")
                    if butSched.cget("text") == "Save Diary":
                        butSched.config(text="Set schedule for tomorrow")
                    break

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Diary(
            id INTEGER PRIMARY KEY,
            date DATE NOT NULL,
            grateful TEXT,
            plan TEXT,
            affirmation TEXT,
            deed TEXT,
            improvement TEXT,
            experiences TEXT,
            day DATE);
            """)

            cursor.execute('SELECT date FROM Diary ORDER BY id DESC LIMIT 1')
            latestDiary = cursor.fetchall()
            if latestDiary == []:
                cursor.execute(
                    "INSERT INTO Diary(date, grateful, plan, affirmation, deed, improvement, experiences, day) VALUES (?, ?, ?, ?,?,?,?,?)",
                    (now.strftime("%d-%B-%Y"), "1.\n2.\n3.", "", "", "", "", "1.\n2.\n3.", now.strftime("%A")))
                cursor.execute('SELECT * FROM Diary ORDER BY id DESC LIMIT 1')
                diary = cursor.fetchall()

                currentDSel = diary
            elif latestDiary[0][0] != now.strftime("%d-%B-%Y"):
                cursor.execute(
                    "INSERT INTO Diary(date, grateful, plan, affirmation, deed, improvement, experiences, day) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (now.strftime("%d-%B-%Y"), "1.\n2.\n3.", "", "", "", "", "1.\n2.\n3.", now.strftime("%A")))
                cursor.execute('SELECT * FROM Diary ORDER BY id DESC LIMIT 1')
                diary = cursor.fetchall()
                currentDSel = diary
            else:
                cursor.execute('SELECT * FROM Diary ORDER BY id DESC LIMIT 1')
                diary = cursor.fetchall()
                currentDSel = diary

            lblDay.config(text=f"Diary entry for: {diary[0][8]}")
            lblDate.config(text=diary[0][1])

            gratefulTxt.delete(1.0, "end")
            if diary[0][2] != "":
                gratefulTxt.insert(1.0, diary[0][2])
            planTxt.delete(1.0, "end")
            if diary[0][3] != "":
                planTxt.insert(1.0, diary[0][3])
            affirmationTxt.delete(1.0, "end")
            if diary[0][4] != "":
                affirmationTxt.insert(1.0, diary[0][4])
            deedTxt.delete(1.0, "end")
            if diary[0][5] != "":
                deedTxt.insert(1.0, diary[0][5])
            improveTxt.delete(1.0, "end")
            if diary[0][6] != "":
                improveTxt.insert(1.0, diary[0][6])
            experiencesTxt.delete(1.0, "end")
            if diary[0][7] != "":
                experiencesTxt.insert(1.0, diary[0][7])

            db.commit()

            butSave = Button(diaryWindow, text="Save", command=partial(updateDiary, currentDSel))
            butSave.pack(padx=10, pady=5, side=TOP)

            def diariesScreen():
                for widget in diaryWindow.winfo_children():
                    if ".!toplevel.!toplevel" in str(widget):
                        exists = True
                        if exists:
                            widget.destroy()

                diaryBookScreen = Toplevel(diaryWindow)
                diaryBookScreen.title("Your diary")
                app_width = 500
                app_height = 500
                x = (screen_width / 2) - (app_width / 2)
                y = (screen_height / 2) - (app_height / 2)
                diaryBookScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

                topDiaryList = Frame(diaryBookScreen, width=500, height=100)
                topDiaryList.pack()
                botDiaryList = Frame(diaryBookScreen)
                botDiaryList.pack(expand=TRUE, fill=BOTH)
                cursor.execute('SELECT * FROM diary')
                diariesArr = cursor.fetchall()
                if diariesArr == []:
                    notify()
                    return
                cursor.execute('SELECT id FROM diary')
                diariesIdList = cursor.fetchall()

                dayCounter = len(diariesIdList) - 1
                todayId = diariesArr[dayCounter][0]

                cursor.execute('SELECT * FROM diary WHERE id = ?', (todayId,))
                todayDiary = cursor.fetchall()

                def dayCounterBack(input):
                    dayCounter = input - 1
                    todayId = diariesArr[dayCounter][0]
                    cursor.execute('SELECT * FROM diary WHERE id = ?', (todayId,))
                    todayDiary = cursor.fetchall()
                    lblToday.config(text=todayDiary[0][1])

                    if input <= 1:
                        butYesterday.config(text="")
                    else:
                        yesterdayId = diariesArr[dayCounter - 1][0]
                        cursor.execute('SELECT * FROM diary WHERE id = ?', (yesterdayId,))
                        yesterdayDiary = cursor.fetchall()
                        butYesterday.config(text=yesterdayDiary[0][1], command=partial(dayCounterBack, dayCounter))

                    tomorrowId = diariesArr[dayCounter + 1][0]
                    cursor.execute('SELECT * FROM diary WHERE id = ?', (tomorrowId,))
                    tomorrowDiary = cursor.fetchall()
                    butTomorrow.config(text=tomorrowDiary[0][1], command=partial(dayCounterForward, dayCounter))
                    diariesTxt.delete(1.0, "end")
                    strDiary = f"Date: {diariesArr[dayCounter][8]}\n{diariesArr[dayCounter][1]}\n"
                    if diariesArr[dayCounter][2] != "1.\n2.\n3.":
                        strDiary += f"\nI am grateful for:\n{diariesArr[dayCounter][2]}\n"
                    if diariesArr[dayCounter][3] != "":
                        strDiary += f"\nThis is how I will make today great:\n{diariesArr[dayCounter][3]}\n"
                    affirmationTxt.delete(1.0, "end")
                    if diariesArr[dayCounter][4] != "":
                        strDiary += f"\nPositive affirmation:\n{diariesArr[dayCounter][4]}\n"
                    if diariesArr[dayCounter][5] != "":
                        strDiary += f"\nMy good deed for today:\n{diariesArr[dayCounter][5]}\n"
                    if diariesArr[dayCounter][6] != "":
                        strDiary += f"\nHow I'll improve:\n{diariesArr[dayCounter][6]}\n"
                    if diariesArr[dayCounter][7] != "1.\n2.\n3.":
                        strDiary += f"\nGreat things I experienced today:\n{diariesArr[dayCounter][7]}"
                    diariesTxt.insert(1.0, strDiary)

                def dayCounterForward(input):
                    dayCounter = input + 1
                    todayId = diariesArr[dayCounter][0]

                    cursor.execute('SELECT * FROM diary WHERE id = ?', (todayId,))
                    todayDiary = cursor.fetchall()
                    lblToday.config(text=todayDiary[0][1])

                    if len(diariesIdList) - 2 <= input:
                        butTomorrow.config(text="")
                    else:
                        tomorrowId = diariesArr[dayCounter + 1][0]
                        cursor.execute('SELECT * FROM diary WHERE id = ?', (tomorrowId,))
                        tomorrowDiary = cursor.fetchall()
                        butTomorrow.config(text=tomorrowDiary[0][1], command=partial(dayCounterForward, dayCounter))

                    yesterdayId = diariesArr[dayCounter - 1][0]
                    cursor.execute('SELECT * FROM diary WHERE id = ?', (yesterdayId,))
                    yesterdayDiary = cursor.fetchall()
                    butYesterday.config(text=yesterdayDiary[0][1], command=partial(dayCounterBack, dayCounter))
                    diariesTxt.delete(1.0, "end")
                    strDiary = f"Date: {diariesArr[dayCounter][8]}\n{diariesArr[dayCounter][1]}\n"
                    if diariesArr[dayCounter][2] != "1.\n2.\n3.":
                        strDiary += f"\nI am grateful for:\n{diariesArr[dayCounter][2]}\n"
                    if diariesArr[dayCounter][3] != "":
                        strDiary += f"\nThis is how I will make today great:\n{diariesArr[dayCounter][3]}\n"
                    affirmationTxt.delete(1.0, "end")
                    if diariesArr[dayCounter][4] != "":
                        strDiary += f"\nPositive affirmation:\n{diariesArr[dayCounter][4]}\n"
                    if diariesArr[dayCounter][5] != "":
                        strDiary += f"\nMy good deed for today:\n{diariesArr[dayCounter][5]}\n"
                    if diariesArr[dayCounter][6] != "":
                        strDiary += f"\nHow I'll improve:\n{diariesArr[dayCounter][6]}\n"
                    if diariesArr[dayCounter][7] != "1.\n2.\n3.":
                        strDiary += f"\nGreat things I experienced today:\n{diariesArr[dayCounter][7]}"
                    diariesTxt.insert(1.0, strDiary)

                butYesterday = Button(diaryBookScreen, text="", command=partial(dayCounterBack, dayCounter))
                butYesterday.pack(in_=topDiaryList, pady=5, padx=10, side=LEFT)

                if len(diariesIdList) < 2:
                    pass
                else:
                    yesterdayId = diariesArr[dayCounter - 1][0]
                    cursor.execute('SELECT * FROM diary WHERE id = ?', (yesterdayId,))
                    yesterdayDiary = cursor.fetchall()
                    butYesterday.config(text=yesterdayDiary[0][1])

                lblToday = Label(diaryBookScreen, text=todayDiary[0][1])
                lblToday.pack(in_=topDiaryList, pady=5, padx=10, side=LEFT)

                butTomorrow = Button(diaryBookScreen, text="")
                butTomorrow.pack(in_=topDiaryList, pady=5, padx=10, side=LEFT)

                diariesTxt = Text(diaryBookScreen, wrap=WORD, height=20, undo=TRUE)
                diariesTxt.pack(in_=botDiaryList, pady=5, padx=10, expand=TRUE, fill=BOTH)

                # ALL FUNCTION SUPER IMPORTANT
                '''diariesTxt.delete(1.0, "end")
                for i in range(0, len(diariesArr)):
                    diaryDay = diariesArr[i]
                    print(diaryDay)
                    strDiary = f"Date: {diariesArr[dayCounter][8]}\n{diaryDay[1]}\n"
                    if diaryDay[2] != "":
                        strDiary += f"\nI am grateful for:\n{diaryDay[2]}\n"
                    if diaryDay[3] != "":
                        strDiary += f"\nThis is how I will make today great:\n{diaryDay[3]}\n"
                    affirmationTxt.delete(1.0, "end")
                    if diaryDay[4] != "":
                            strDiary += f"\nPositive affirmation:\n{diaryDay[4]}\n"
                    if diaryDay[5] != "":
                        strDiary += f"\nMy good deed for today:\n{diaryDay[5]}\n"
                    if diaryDay[6] != "":
                        strDiary += f"\nHow I'll improve:\n{diaryDay[6]}\n"
                    if diaryDay[7] != "":
                        strDiary += f"\nGreat things I experienced today:\n{diaryDay[7]}"
                    diariesTxt.insert(1.0, strDiary)'''

                diariesTxt.delete(1.0, "end")

                strDiary = f"Date: {diariesArr[dayCounter][8]}\n{diariesArr[dayCounter][1]}\n"
                if diariesArr[dayCounter][2] != "1.\n2.\n3.":
                    strDiary += f"\nI am grateful for:\n{diariesArr[dayCounter][2]}\n"
                if diariesArr[dayCounter][3] != "":
                    strDiary += f"\nThis is how I will make today great:\n{diariesArr[dayCounter][3]}\n"
                affirmationTxt.delete(1.0, "end")
                if diariesArr[dayCounter][4] != "":
                    strDiary += f"\nPositive affirmation:\n{diariesArr[dayCounter][4]}\n"
                if diariesArr[dayCounter][5] != "":
                    strDiary += f"\nMy good deed for today:\n{diariesArr[dayCounter][5]}\n"
                if diariesArr[dayCounter][6] != "":
                    strDiary += f"\nHow I'll improve:\n{diariesArr[dayCounter][6]}\n"
                if diariesArr[dayCounter][7] != "1.\n2.\n3.":
                    strDiary += f"\nGreat things I experienced today:\n{diariesArr[dayCounter][7]}"
                diariesTxt.insert(1.0, strDiary)

            butDiaries = Button(diaryWindow, text="Your Diary", font=("Helvetica", 14), command=diariesScreen)
            butDiaries.pack(side=TOP)

            def doneCom():
                option = messagebox.askyesno("Quit",
                                             "Are you sure you want to return to the main screen? \n \n Unsaved changes will be lost.")
                if option:
                    diaryWindow.destroy()

            butDone = Button(diaryWindow, text="Back", font=("Helvetica", 14), command=doneCom)
            butDone.pack(side=TOP, padx=10, pady=10)

            diaryWindow.protocol("WM_DELETE_WINDOW", partial(on_closing, diaryWindow))

        butDiary = Button(topframe, text="Diary", font=("Arial", 10), command=diaryScreen)
        butDiary.pack()

        def goalScreen():
            for widget in window.winfo_children():
                if ".!toplevel" in str(widget):
                    exits = True
                    if exits:
                        widget.destroy()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Goals(
            id INTEGER PRIMARY KEY,
            short TEXT,
            long TEXT,
            need TEXT,
            want TEXT);
            """)

            goalsWindow = Toplevel(window)
            goalsWindow.title("Your Goals")
            app_width = int(screen_width / 2)
            app_height = int(screen_height * 0.95)
            x = (screen_width / 2) - (app_width / 2)
            y = (screen_height / 2) - (app_height / 2)
            goalsWindow.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
            top = Frame(goalsWindow)
            top.pack()

            lblShort = Label(goalsWindow, text="Short-term goals: ", font=("Arial", 14))
            lblShort.pack(in_=top, side=TOP, pady=5)

            shortTxt = Text(goalsWindow, wrap=WORD, height=12, undo=TRUE)
            shortTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

            lblLong = Label(goalsWindow, text="Long-term goals: ", font=("Arial", 14))
            lblLong.pack(in_=top, side=TOP, pady=5)

            longTxt = Text(goalsWindow, wrap=WORD, height=10, undo=TRUE)
            longTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

            lblNeed = Label(goalsWindow, text="Things I need: ", font=("Arial", 14))
            lblNeed.pack(in_=top, side=TOP, pady=5)

            needTxt = Text(goalsWindow, wrap=WORD, height=8, undo=TRUE)
            needTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

            lblWant = Label(goalsWindow, text="Things I want: ", font=("Arial", 14))
            lblWant.pack(in_=top, side=TOP, pady=5)

            wantTxt = Text(goalsWindow, wrap=WORD, height=8, undo=TRUE)
            wantTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

            cursor.execute('SELECT * FROM Goals')
            goalArr = cursor.fetchall()
            if goalArr == []:
                insert_fields = """INSERT INTO Goals(short, long, need, want)
                                        VALUES (?, ?, ?, ?)"""
                cursor.execute(insert_fields, ("", "", "", ""))
                pass
            else:
                shortTxt.delete(1.0, "end")
                if goalArr[0][1] != "":
                    shortTxt.insert(1.0, goalArr[0][1])
                longTxt.delete(1.0, "end")
                if goalArr[0][2] != "":
                    longTxt.insert(1.0, goalArr[0][2])
                wantTxt.delete(1.0, "end")
                if goalArr[0][3] != "":
                    wantTxt.insert(1.0, goalArr[0][3])
                needTxt.delete(1.0, "end")
                if goalArr[0][4] != "":
                    needTxt.insert(1.0, goalArr[0][4])

            def updateGoals():
                while True:
                    id = 1
                    short = shortTxt.get("1.0", 'end-1c')
                    long = longTxt.get("1.0", 'end-1c')
                    need = needTxt.get("1.0", 'end-1c')
                    want = wantTxt.get("1.0", 'end-1c')

                    sql = "UPDATE Goals SET short =?, long =?, need = ?, want = ? WHERE id = ?"

                    cursor.execute(sql, (short, long, need, want, id,))
                    db.commit()
                    messagebox.showinfo("Success", f"Your goals were successfully updated!")

                    db.commit()
                    break

            butSave = Button(goalsWindow, text="Save", command=updateGoals)
            butSave.pack(padx=10, pady=5, side=TOP)

            def doneCom():
                option = messagebox.askyesno("Quit",
                                             "Are you sure you want to return to the main screen? \n \n Unsaved "
                                             "changes will be lost.")
                if option:
                    goalsWindow.destroy()

            butDone = Button(goalsWindow, text="Back", font=("Helvetica", 14), command=doneCom)
            butDone.pack(side=TOP, padx=10, pady=10)

            goalsWindow.protocol("WM_DELETE_WINDOW", partial(on_closing, goalsWindow))

        butGoals = Button(topframe, text="Goals", font=("Arial", 10), command=goalScreen)
        butGoals.pack()

        def feedBack():
            for widget in window.winfo_children():
                if ".!toplevel" in str(widget):
                    exits = True
                    if exits:
                        widget.destroy()

            est_duration = 0
            sched_duration = 0
            completed_tasks = []
            uncompleted_tasks = []

            total_tasks = len(arrayF)
            for y in range(len(arrayF)):
                est_duration += arrayF[y][2]

            for i in range(len(completedTasks)):
                sched_duration += completedTasks[i].duration
                if completedTasks[i].completed == True:
                    completed_tasks.append(f"{i + 1}. {completedTasks[i].name} - {completedTasks[i].duration} minutes")
                else:
                    uncompleted_tasks.append(
                        f"{i + 1}. {completedTasks[i].name} - {completedTasks[i].duration} minutes")

            hour = int(est_duration / 60)
            minutes = est_duration % 60

            est_duration = ""
            if hour > 9:
                est_duration = f"{est_duration}{hour}"
            else:
                est_duration = f"0{est_duration}{hour}"
            if minutes > 9:
                est_duration = f"{est_duration}:{minutes}"
            else:
                est_duration = f"{est_duration}:0{minutes}"

            feedBackScreen = Toplevel(window)
            feedBackScreen.title("Breakdown of your schedule")
            widt = int(screen_width / 2)
            app_width = widt
            app_height = int(screen_height)
            x = (screen_width / 2) - (app_width / 2)
            y = (screen_height / 2) - (app_height / 2)
            feedBackScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

            lblEst = Label(feedBackScreen, text=f"Estimated duration of schedule: {est_duration}")
            lblEst.pack(pady=5, padx=5)

            lblTook = Label(feedBackScreen, text=f"Actual duration of schedule: {sched_duration}")
            lblTook.pack(pady=5, padx=5)

            lblTotalTask = Label(feedBackScreen, text=f"Total tasks: {total_tasks}")
            lblTotalTask.pack(pady=5, padx=5)

            lblCompleted = Label(feedBackScreen, text=f"Total tasks completed: {len(completed_tasks)}")
            lblCompleted.pack(pady=5, padx=5)

            listCompleted = Listbox(feedBackScreen, selectmode=BROWSE)
            listCompleted.pack(fill=BOTH, pady=10, padx=20)

            lblUncomplete = Label(feedBackScreen, text=f"Tasks not completed: {len(uncompleted_tasks)}")
            lblUncomplete.pack(pady=5, padx=5)

            listUncompleted = Listbox(feedBackScreen, selectmode=BROWSE)
            listUncompleted.pack(fill=BOTH, pady=10, padx=20)

            for i in range(len(completed_tasks)):
                listCompleted.insert(i, f"{completed_tasks[i]}")

            for i in range(len(uncompleted_tasks)):
                listUncompleted.insert(i, f"{uncompleted_tasks[i]}")

            def doneCom():
                '''option = messagebox.askyesno("Quit",
                                             "Are you sure you want to return to the main screen?")
                if option:'''
                feedBackScreen.destroy()

            butDone = Button(feedBackScreen, text="Back", font=("Helvetica", 14), command=doneCom)
            butDone.pack(side=TOP, padx=10, pady=10)

        feedback = Button(topframe, text="Feedback", font=("Arial", 10), command=feedBack)
        feedback.pack()

        def vocabulary():
            for widget in window.winfo_children():
                if ".!toplevel" in str(widget):
                    exists = True
                    if exists:
                        widget.destroy()

            VocabScreen = Toplevel(window)
            VocabScreen.title("Add a word to your vocabulary")
            app_width = 300
            app_height = 300
            x = (screen_width / 2) - (app_width / 2)
            y = (screen_height / 2) - (app_height / 2)
            VocabScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

            lblWord = Label(VocabScreen, text="Add a word to your vocabulary:")
            lblWord.pack(padx=10, pady=5, side=TOP)

            entWord = Entry(VocabScreen)
            entWord.pack(padx=10, pady=5, side=TOP)

            def addWord():
                addVocabAdd.config(text="Finding Word", state=DISABLED)
                enteredWord = entWord.get()
                if enteredWord == "":
                    messagebox.showinfo("No match", "Please enter a word into the text field.")
                elif " " in enteredWord:
                    messagebox.showinfo("Multiple words", "Please enter a single word into the text field.")
                else:
                    while True:
                        meaning = ""
                        try:
                            meaning += f"Noun : {dictionary.meaning(enteredWord, disable_errors=True)['Noun'][0]} \n"
                        except Exception:
                            pass
                        try:
                            meaning += f"Verb : {dictionary.meaning(enteredWord, disable_errors=True)['Verb'][0]} \n"
                        except Exception:
                            pass
                        try:
                            meaning += f"Adjective : {dictionary.meaning(enteredWord, disable_errors=True)['Adjective'][0]} \n"
                        except Exception:
                            try:
                                meaning += f"Adverb : {dictionary.meaning(enteredWord, disable_errors=True)['Adverb'][0]} \n"
                            except Exception:
                                try:
                                    meaning += f"Pronoun : {dictionary.meaning(enteredWord, disable_errors=True)['Pronoun'][0]} \n"
                                except Exception:
                                    try:
                                        meaning += f"Preposition : {dictionary.meaning(enteredWord, disable_errors=True)['Preposition'][0]} \n"
                                    except Exception:
                                        try:
                                            meaning += f"Conjunction : {dictionary.meaning(enteredWord, disable_errors=True)['Conjunction'][0]} \n"
                                        except Exception:
                                            try:
                                                meaning += f"Interjection : {dictionary.meaning(enteredWord, disable_errors=True)['Interjection'][0]} \n"
                                            except Exception:
                                                pass
                        if meaning == "":
                            messagebox.showinfo("No match", "Definition for entered word can not be found.")
                            break
                        else:
                            with open('Vocabulary.txt', 'a+') as vocabTxtF:
                                vocabTxtF.write(f"{enteredWord} - {meaning}\n")

                            '''bookVocabulary.insert(1.0, f"{enteredWord} - {meaning}\n")
                            entWord.delete(0, 'end')
                            id = currentSel[0][0]
                            vocabulary = bookVocabulary.get("1.0", 'end-1c')
    
                            sql = "UPDATE Books SET vocabulary = ? WHERE id = ?"
    
                            cursor.execute(sql, (vocabulary, id,))
                            db.commit()'''
                        break
                addVocabAdd.config(text="Search word", state=NORMAL)
                entWord.delete(0, 'end')

            def startV():
                v = threading.Thread(name='findWord', target=addWord, daemon=True)
                v.start()

            addVocabAdd = Button(VocabScreen, text="Search word", command=startV)
            addVocabAdd.pack()

            def vocabRepo():
                for widget in VocabScreen.winfo_children():
                    if ".!toplevel.!toplevel" in str(widget):
                        exists = True
                        if exists:
                            widget.destroy()
                vocRepoScreen = Toplevel(VocabScreen)
                vocRepoScreen.title("List of words in vocabulary")
                app_width = 500
                app_height = 500
                x = (screen_width / 2) - (app_width / 2)
                y = (screen_height / 2) - (app_height / 2)
                vocRepoScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

                vocabTxt = Text(vocRepoScreen, wrap=WORD, height=20, undo=TRUE)
                vocabTxt.pack(pady=5, padx=10, expand=TRUE, fill=BOTH)

                vocabTxt.delete(1.0, "end")

                Content = ""
                try:
                    with open('Vocabulary.txt', 'r') as vocabTxtF:
                        for line in vocabTxtF:
                            Content += line
                except Exception:
                    pass

                if Content != "\n":
                    vocabTxt.insert(1.0, f"{Content}")

                def saveVoc():
                    with open('Vocabulary.txt', 'w') as vocabTxtF:
                        vocabTxtF.write(f"{vocabTxt.get(1.0, END)}")
                    messagebox.showinfo("Successfully saved", f"Successfully saved vocabulary.")

                nav_vocab = Menu(vocRepoScreen)
                vocRepoScreen.config(menu=nav_vocab)

                navigate_vocab = Menu(nav_vocab)
                nav_vocab.add_cascade(label="File", menu=navigate_vocab)

                navigate_vocab.add_command(label="Save", command=saveVoc)

                if vocabTxt.get(1.0, "end-1c") == "":
                    messagebox.showwarning("Empty vocabulary",
                                           "Your vocabulary is empty!\nAdd a word by clicking the Search word button.")
                    vocRepoScreen.destroy()
                    return

            vocabRepo = Button(VocabScreen, text="Your Vocabulary", command=vocabRepo)
            vocabRepo.pack()

            def desVoc():
                VocabScreen.destroy()

            btnBack = Button(VocabScreen, text="Back", command=desVoc)
            btnBack.pack(padx=10, pady=5, side=TOP)

        vocab = Button(topframe, text="Vocabulary", font=("Arial", 10), command=vocabulary)
        vocab.pack()

        def notes():
            for widget in window.winfo_children():
                if ".!toplevel" in str(widget):
                    exists = True
                    if exists:
                        widget.destroy()

            noteScreen = Toplevel(window)
            noteScreen.title("Notes Repository")
            app_width = 500
            app_height = 500
            x = (screen_width / 2) - (app_width / 2)
            y = (screen_height / 2) - (app_height / 2)
            noteScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

            lblNotes = Label(noteScreen, text="Your Notes:")
            lblNotes.pack(padx=10, pady=5, side=TOP)

            notesList = Listbox(noteScreen, selectmode=BROWSE)
            notesList.pack(fill=BOTH, pady=10, padx=10)

            notesList.delete(0, END)

            if not os.path.exists("Notes"):
                os.mkdir('Notes')

            textFileF = []
            textFile = os.listdir("Notes")
            for i in range(0, len(textFile)):
                if textFile[i].endswith('.txt'):
                    textFileF.append(textFile[i])

            for y in range(0, len(textFileF)):
                notesList.insert(y, f"{textFileF[y]}")

            def newNote():
                while True:
                    title = simpledialog.askstring("Note tile", "Please enter title for new note: ")
                    if title == "":
                        messagebox.showinfo("No match", "Please enter a title into the title field.")
                        continue
                    elif title == None:
                        break
                    elif os.path.exists(f"Notes/{title}.txt"):
                        messagebox.showwarning(noteScreen,
                                               "Title for note already exists.\n Please enter a different title.")
                        continue
                    else:
                        with open(f'Notes/{title}.txt', 'w+') as createdNote:
                            createdNote.write("")

                        for widget in noteScreen.winfo_children():
                            if ".!toplevel.!toplevel" in str(widget):
                                exists = True
                                if exists:
                                    widget.destroy()
                        noteRepScreen = Toplevel(noteScreen)
                        noteRepScreen.title(f"{title}.txt")
                        app_width = 500
                        app_height = 500
                        x = (screen_width / 2) - (app_width / 2)
                        y = (screen_height / 2) - (app_height / 2)
                        noteRepScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

                        noteTxt = Text(noteRepScreen, wrap=WORD, height=20, undo=TRUE)
                        noteTxt.pack(pady=5, padx=10, expand=TRUE, fill=BOTH)

                        def saveNote():
                            Content = noteTxt.get(1.0, END)
                            with open(f'Notes/{title}.txt', 'w+') as savedNote:
                                savedNote.write(Content)
                            messagebox.showinfo("Successfully saved", f"Successfully saved note: {title}")

                        notesList.insert(END, f'{title}.txt')

                        noteRepScreen.protocol("WM_DELETE_WINDOW", partial(on_closing, noteRepScreen))

                    nav_note = Menu(noteRepScreen)
                    noteRepScreen.config(menu=nav_note)

                    navigate_note = Menu(nav_note)
                    nav_note.add_cascade(label="File", menu=navigate_note)
                    navigate_note.add_command(label="Save", command=saveNote)

                    break


            btnNote = Button(noteScreen, text="Create new note", command=newNote)
            btnNote.pack(padx=10, pady=5, side=TOP)

            def openNote():
                if notesList.curselection() == ():
                    messagebox.showwarning("showwarning", "Please select or create a new note.")
                    return
                else:
                    title = notesList.get(notesList.curselection())
                    Content = ""
                    with open(f'Notes/{title}', 'r+') as editNote:
                        for line in editNote:
                            Content += line

                    for widget in noteScreen.winfo_children():
                        if ".!toplevel.!toplevel" in str(widget):
                            exists = True
                            if exists:
                                widget.destroy()
                    openScreen = Toplevel(noteScreen)
                    openScreen.title(f"{title}")
                    app_width = 500
                    app_height = 500
                    x = (screen_width / 2) - (app_width / 2)
                    y = (screen_height / 2) - (app_height / 2)
                    openScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

                    openTxt = Text(openScreen, wrap=WORD, height=20, undo=TRUE)
                    openTxt.pack(pady=5, padx=10, expand=TRUE, fill=BOTH)

                    openTxt.insert(1.0, Content)

                    openScreen.protocol("WM_DELETE_WINDOW", partial(on_closing, openScreen))

                    def saveNote():
                        Content = openTxt.get(1.0, END)
                        with open(f'Notes/{title}', 'w+') as savedNote:
                            savedNote.write(Content)
                        messagebox.showinfo("Successfully saved", f"Successfully saved note: {title}")

                nav_note = Menu(noteScreen)
                noteScreen.config(menu=nav_note)

                navigate_note = Menu(nav_note)
                nav_note.add_cascade(label="File", menu=navigate_note)
                navigate_note.add_command(label="Save", command=saveNote)

            btnOpen = Button(noteScreen, text="Open note", command=openNote)
            btnOpen.pack(padx=10, pady=5, side=TOP)

            def deleteNote():
                if notesList.curselection() == ():
                    messagebox.showwarning("showwarning", "Please select a note.")
                    return
                else:
                    title = notesList.get(notesList.curselection())
                    deletingNote = messagebox.askyesno("Delete file",
                                                       f"Are you sure you want to delete note: {title}")
                    if deletingNote:
                        os.remove(f'Notes/{title}')
                        notesList.delete(notesList.curselection())

            btnDelete = Button(noteScreen, text="Delete note", command=deleteNote)
            btnDelete.pack(padx=10, pady=5, side=TOP)

            def desNote():
                noteScreen.destroy()

            btnBack = Button(noteScreen, text="Back", command=desNote)
            btnBack.pack(padx=10, pady=5, side=TOP)

        noteBtn = Button(topframe, text="Notes", font=("Arial", 10), command=notes)
        noteBtn.pack()

        def monthlyDoc():
            for widget in window.winfo_children():
                if ".!toplevel" in str(widget):
                    exists = True
                    if exists:
                        widget.destroy()

            monthScreen = Toplevel(window)
            today = datetime.now()
            month = today.strftime("%B")
            monthScreen.title(f"Monthly Report: {month}")
            app_width = 600
            app_height = 800
            x = (screen_width / 2) - (app_width / 2)
            y = (screen_height / 2) - (app_height / 2)
            monthScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS Months(
                           id INTEGER PRIMARY KEY,
                           month TEXT NOT NULL,
                           question TEXT,
                           note TEXT);
                           """)

            selections = []

            cursor.execute("SELECT id, question, note FROM Months WHERE month = ?", (today.strftime("%m/%Y"),))

            responseF = cursor.fetchall()

            if responseF != []:
                currentID = responseF[0][0]
                allQuestions = responseF[0][1]
                note = responseF[0][2]
            else:
                cursor.execute("INSERT INTO Months (month, question, note) VALUES (?, ?, ?)", (today.strftime("%m/%Y"),
                                                                                               "", ""))
                currentID = 1
                allQuestions = ""

            allQuestionsF = re.sub(pattern, ' ', allQuestions)

            allQuestionsArr = allQuestionsF.split()

            monthFrame = Frame(monthScreen)
            monthFrame.pack(pady=5)

            txtComment = Text(monthFrame, wrap=WORD, height=10, undo=TRUE)
            txtComment.grid(pady=3, padx=3, row=21, column=0, columnspan=2)

            if len(allQuestionsArr) < 2:
                for y in range(0, 20):
                    selections.append(f"Selection{y + 1}")
                    selections[y] = IntVar()
            else:
                for y in range(0, len(allQuestionsArr)):
                    selections.append(f"Selection{y + 1}")
                    selections[y] = IntVar()
                    selections[y].set(allQuestionsArr[y])
                    txtComment.delete(1.0, END)
                    txtComment.insert(1.0, note)

            option = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

            Questions = ["Overall Mood", "Gratitude", "Mindfulness", "Family", "Friends", "Partnership", "Having fun",
                         "Calm and Serenity", "Time for You", "Eating Healthy", "Drinking Water",
                         "Exercise and Movement", "Going Outside", "Health", "Creativity", "Finances",
                         "Work and Education", "Thoughts and Emotions", "The Present", "The Future"]

            lblQues = Label(monthFrame, text="Overall Mood: ")
            lblQues.grid(pady=3, padx=10, row=0, column=0)

            dropSel = OptionMenu(monthFrame, selections[0], *option)
            dropSel.grid(pady=3, padx=10, row=0, column=1)

            lblQues = Label(monthFrame, text="Gratitude: ")
            lblQues.grid(pady=3, padx=10, row=1, column=0)

            dropSel = OptionMenu(monthFrame, selections[1], *option)
            dropSel.grid(pady=3, padx=10, row=1, column=1)

            lblQues = Label(monthFrame, text="Mindfulness: ")
            lblQues.grid(pady=3, padx=10, row=2, column=0)

            dropSel = OptionMenu(monthFrame, selections[2], *option)
            dropSel.grid(pady=3, padx=10, row=2, column=1)

            lblQues = Label(monthFrame, text="Family: ")
            lblQues.grid(pady=3, padx=10, row=3, column=0)

            dropSel = OptionMenu(monthFrame, selections[3], *option)
            dropSel.grid(pady=3, padx=10, row=3, column=1)

            lblQues = Label(monthFrame, text="Friends: ")
            lblQues.grid(pady=3, padx=10, row=4, column=0)

            dropSel = OptionMenu(monthFrame, selections[4], *option)
            dropSel.grid(pady=3, padx=10, row=4, column=1)

            lblQues = Label(monthFrame, text="Partnership: ")
            lblQues.grid(pady=3, padx=10, row=5, column=0)

            dropSel = OptionMenu(monthFrame, selections[5], *option)
            dropSel.grid(pady=3, padx=10, row=5, column=1)

            lblQues = Label(monthFrame, text="Having fun: ")
            lblQues.grid(pady=3, padx=10, row=6, column=0)

            dropSel = OptionMenu(monthFrame, selections[6], *option)
            dropSel.grid(pady=3, padx=10, row=6, column=1)

            lblQues = Label(monthFrame, text="Calm and Serenity: ")
            lblQues.grid(pady=3, padx=10, row=7, column=0)

            dropSel = OptionMenu(monthFrame, selections[7], *option)
            dropSel.grid(pady=3, padx=10, row=7, column=1)

            lblQues = Label(monthFrame, text="Time for You: ")
            lblQues.grid(pady=3, padx=10, row=8, column=0)

            dropSel = OptionMenu(monthFrame, selections[8], *option)
            dropSel.grid(pady=3, padx=10, row=8, column=1)

            lblQues = Label(monthFrame, text="Eating Healthy: ")
            lblQues.grid(pady=3, padx=10, row=9, column=0)

            dropSel = OptionMenu(monthFrame, selections[9], *option)
            dropSel.grid(pady=3, padx=10, row=9, column=1)

            lblQues = Label(monthFrame, text="Drinking Water: ")
            lblQues.grid(pady=3, padx=10, row=10, column=0)

            dropSel = OptionMenu(monthFrame, selections[10], *option)
            dropSel.grid(pady=3, padx=10, row=10, column=1)

            lblQues = Label(monthFrame, text="Exercise and Movement: ")
            lblQues.grid(pady=3, padx=10, row=11, column=0)

            dropSel = OptionMenu(monthFrame, selections[11], *option)
            dropSel.grid(pady=3, padx=10, row=11, column=1)

            lblQues = Label(monthFrame, text="Going Outside: ")
            lblQues.grid(pady=3, padx=10, row=12, column=0)

            dropSel = OptionMenu(monthFrame, selections[12], *option)
            dropSel.grid(pady=3, padx=10, row=12, column=1)

            lblQues = Label(monthFrame, text="Health: ")
            lblQues.grid(pady=3, padx=10, row=13, column=0)

            dropSel = OptionMenu(monthFrame, selections[13], *option)
            dropSel.grid(pady=3, padx=10, row=13, column=1)

            lblQues = Label(monthFrame, text="Creativity ")
            lblQues.grid(pady=3, padx=10, row=14, column=0)

            dropSel = OptionMenu(monthFrame, selections[14], *option)
            dropSel.grid(pady=3, padx=10, row=14, column=1)

            lblQues = Label(monthFrame, text="Finances: ")
            lblQues.grid(pady=3, padx=10, row=15, column=0)

            dropSel = OptionMenu(monthFrame, selections[15], *option)
            dropSel.grid(pady=3, padx=10, row=15, column=1)

            lblQues = Label(monthFrame, text="Work and Education: ")
            lblQues.grid(pady=3, padx=10, row=16, column=0)

            dropSel = OptionMenu(monthFrame, selections[16], *option)
            dropSel.grid(pady=3, padx=10, row=16, column=1)

            lblQues = Label(monthFrame, text="Thoughts and Emotions: ")
            lblQues.grid(pady=3, padx=10, row=17, column=0)

            dropSel = OptionMenu(monthFrame, selections[17], *option)
            dropSel.grid(pady=3, padx=10, row=17, column=1)

            lblQues = Label(monthFrame, text="The Present: ")
            lblQues.grid(pady=3, padx=10, row=18, column=0)

            dropSel = OptionMenu(monthFrame, selections[18], *option)
            dropSel.grid(pady=3, padx=10, row=18, column=1)

            lblQues = Label(monthFrame, text="The Future: ")
            lblQues.grid(pady=3, padx=10, row=19, column=0)

            dropSel = OptionMenu(monthFrame, selections[19], *option)
            dropSel.grid(pady=3, padx=10, row=19, column=1)

            lblComment = Label(monthFrame, text="Monthly Notes: ")
            lblComment.grid(pady=3, padx=10, row=20, column=0, sticky=W)

            monthScreen.protocol("WM_DELETE_WINDOW", partial(on_closing, monthScreen))

            questionAnswers = []
            def saveDem():
                for i in range(0, len(selections)):
                    if selections[i].get() == 0:
                        messagebox.showwarning("Choose value", f"Please choose a valid value for question: {Questions[i]}")
                        return
                    questionAnswers.append(selections[i].get())
                cursor.execute("UPDATE Months SET month = ?, question = ?, note = ? WHERE id = ?", (today.strftime("%m/%Y"),
                                                                                               str(questionAnswers), txtComment.get(1.0, END), currentID))
                db.commit()
                messagebox.showinfo("Successfully saved", f"Successfully saved monthly report: {month}")

            def monthRepo():
                for widget in window.winfo_children():
                    if ".!toplevel.!toplevel" in str(widget):
                        exists = True
                        if exists:
                            widget.destroy()

                selectMonthScreen = Toplevel(monthScreen)
                selectMonthScreen.title(f"Choose a month")
                app_width = 300
                app_height = 300
                x = (screen_width / 2) - (app_width / 2)
                y = (screen_height / 2) - (app_height / 2)
                selectMonthScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

                listMonths = Listbox(selectMonthScreen, selectmode=BROWSE)
                listMonths.pack(fill=BOTH, pady=10, padx=20)

                cursor.execute("SELECT month from Months")
                allDates = cursor.fetchall()

                cursor.execute("SELECT question from Months")
                allQF = cursor.fetchall()

                for i in range(0, len(allDates)):
                    try:
                        if allQF[i][0] != "":
                            listMonths.insert(i, str(allDates[i][0]))
                    except:
                        pass

                def selectMonth():
                    choice = listMonths.curselection()
                    if choice == ():
                        messagebox.showwarning("No option selected", "Please select a valid month.")
                    else:

                        selectedMonthScreen = Toplevel(window)
                        selectedMonthScreen.title(f"Date: {listMonths.get(choice)}")
                        app_width = 600
                        app_height = 800
                        x = (screen_width / 2) - (app_width / 2)
                        y = (screen_height / 2) - (app_height / 2)
                        selectedMonthScreen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
                        selectedFrame = Frame(selectedMonthScreen)
                        selectedFrame.pack()

                        cursor.execute("SELECT question, note FROM Months WHERE month = (?)", (listMonths.get(choice),))
                        answerF = cursor.fetchall()

                        answers = answerF[0][0]
                        note = answerF[0][1]

                        allAnswersF = re.sub(pattern, ' ', answers)

                        allQuestionsArr = allAnswersF.split()

                        for i in range(0, len(Questions)):
                            lblQues = Label(selectedFrame, text=f"{Questions[i]}: ")
                            lblQues.grid(pady=3, padx=10, row=i, column=0)

                            lblQuesV = Label(selectedFrame, text=f"{allQuestionsArr[i]}")
                            lblQuesV.grid(pady=3, padx=10, row=i, column=1)

                        lblNote = Label(selectedFrame, text=f"Comments for Month: ")
                        lblNote.grid(pady=3, padx=10, row=21, column=0)

                        txtComment = Text(selectedFrame, height=8)
                        txtComment.grid(padx=3, pady=3, row=22, column=0, columnspan=2)

                        txtComment.insert(1.0, note)

                        selectMonthScreen.destroy()
                        monthScreen.destroy()

                btnSelectMonth = Button(selectMonthScreen, text="Select", command=selectMonth)
                btnSelectMonth.pack()

            save_dem = Menu(monthScreen)
            monthScreen.config(menu=save_dem)

            save_demeanour = Menu(save_dem)
            save_dem.add_cascade(label="File", menu=save_demeanour)
            save_demeanour.add_command(label="Save", command=saveDem)
            save_demeanour.add_separator()
            save_demeanour.add_command(label="All Months", command=monthRepo)

        monthBtn = Button(topframe, text="Monthly Report", font=("Arial", 10), command=monthlyDoc)
        monthBtn.pack()

        def exportDocs():
            directory_loc = filedialog.askdirectory()
            if directory_loc == "":
                return
            else:
                try:
                    shutil.copytree('Notes', f"{directory_loc}/Notes")
                    shutil.copy("Vocabulary.txt", directory_loc)
                    shutil.copy("Scheduler.db", directory_loc)
                    messagebox.showinfo("Successfully exported", f"Successfully exported your data to: {directory_loc}")

                except Exception:
                    print(Exception)
                    messagebox.showwarning("Location error",
                                           "Can not export directory here.\nChoose a different location or make a "
                                           "new directory please.")

        btnExport = Button(window, text="Export Data", command=exportDocs, font=("Arial", 10))
        btnExport.pack(padx=10, pady=5, side=BOTTOM)    

        nav_menu = Menu(window)
        window.config(menu=nav_menu)

        navigate_menu = Menu(nav_menu)
        nav_menu.add_cascade(label="Navigate", menu=navigate_menu)
        navigate_menu.add_command(label="Scheduler", command=modSchedule)
        navigate_menu.add_separator()

        navigate_menu.add_command(label="Books", command=bookScreen)
        navigate_menu.add_command(label="Diary", command=diaryScreen)
        navigate_menu.add_command(label="Goals", command=goalScreen)
        navigate_menu.add_command(label="Feedback", command=feedBack)
        navigate_menu.add_command(label="Vocabulary", command=vocabulary)
        navigate_menu.add_command(label="Notes", command=notes)
        navigate_menu.add_command(label="Monthly Report", command=monthlyDoc)

        def on_closing(screen):
            if messagebox.askokcancel("Quit", "Are sure you want to quit? \n \n Unsaved changes will be lost."):
                if str(screen) == ".":
                    window.withdraw()
                    global start_background
                    start_background = False
                else:
                    screen.destroy()

        window.protocol("WM_DELETE_WINDOW", partial(on_closing, window))

    window.after(2000, scheduleScreen)
    window.mainloop()


if __name__ == '__main__':
    main()
