import re
from tkinter import *
from tkinter import messagebox
from datetime import datetime, timedelta
import threading
import time
import sqlite3
from tkinter import simpledialog
from functools import partial
from PyDictionary import PyDictionary
from PIL import ImageTk, Image


# import requests
splash_win= Tk()

#Set the title of the window
splash_win.title("Splash Screen Example")

#Define the size of the window or frame
splash_win.geometry("+{}+{}".format(380, 140))
splash_win.geometry("680x567")

canvas = Canvas(splash_win, width=680, height=567)
canvas.pack()
img = ImageTk.PhotoImage(Image.open("Narrator.png"))
canvas.create_image(0, 0, anchor=NW, image=img)


def scheduleScreen(splash):
    splash.destroy()
    window = Tk()
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
    global start_background
    global activities
    activities = []
    global minutes
    minutes = []
    cursor.execute("SELECT * FROM activities")
    arrayF = cursor.fetchall()
    orderA = 1
    bigNum = 1

    if len(arrayF) <= 1:
        cursor.execute("INSERT INTO activities(activity, timeA, listPos) VALUES (?, ?, ?)", ("Enter a task", 2, 1))

    for z in range(0, len(arrayF)):
        if arrayF[z][3] > bigNum:
            bigNum = arrayF[z][3]

    while True:
        for yVar in range(0, len(arrayF)):
            for item in range(0, len(arrayF)):
                if arrayF[item][3] == orderA:
                    orderA += 1
                    activities.append(arrayF[item][1])
                    minutes.append(arrayF[item][2])
                else:
                    pass
        if orderA == bigNum + 1:
            break
        else:
            orderA += 1
    global start_background
    start_background = True
    global counterA
    counterA = len(activities)

    window.geometry("+{}+{}".format(500, 200))
    window.geometry("500x500")
    window.title("Create Habits")

    topframe = Frame(window)
    topframe.pack(anchor=CENTER)

    #chkExample = Checkbutton(window)
    #chkExample.pack(in_=topframe)

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

    def next():
        if butNext.cget("text") == "Save Diary":
            messagebox.showwarning("Unsaved diary", "Please save your diary first")
            diaryMorningScreen()
            return
        try:
            if len(activities) == counterA:
                diaryMorningScreen()
                lblAct.config(text="Complete morning diary entry", )
                butNext.config(text=f"Save Diary")
                return
            activity = activities.pop(0)
            lblAct.config(text=activity)
            lblAct.pack()

            aTime = minutes.pop(0)
            alarm_time = now + timedelta(minutes=aTime)
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
        global activities
        activities = []
        global minutes
        minutes = []
        orderA = 1
        bigNum = 1

        if len(arrayF) <= 1:
            cursor.execute("INSERT INTO activities(activity, timeA, listPos) VALUES (?, ?, ?)", ("Enter a task", 2, 1))

        for z in range(0, len(arrayF)):
            if arrayF[z][3] > bigNum:
                bigNum = arrayF[z][3]

        while True:
            for yVar in range(0, len(arrayF)):
                for item in range(0, len(arrayF)):
                    if arrayF[item][3] == orderA:
                        orderA += 1
                        activities.append(arrayF[item][1])
                        minutes.append(arrayF[item][2])
                    else:
                        pass
            if orderA == bigNum + 1:
                break
            else:
                orderA += 1
        global counterA
        counterA = len(activities)

        screen.destroy()

        lblAct.config(text="")

        lblTimeA.config(text="")
        butNext.lift(topframe)
        butNext.config(text="Start your schedule")
        butSched.config(text="Schedule your day", font=("Arial", 12))

    butNext = Button(window, text="Start your schedule", command=next, font=("Arial", 20))
    butNext.pack(in_=topframe)

    def modSchedule():

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

                collision = cursor.fetchall()
                orderList = []
                for c in range(0, len(collision)):
                    orderList.append(str(collision[c][3]))

                matching = [s for s in orderList if str(listPos) in s]
                if not matching:
                    insert_fields = """INSERT INTO activities(activity, timeA, listPos)
                            VALUES (?, ?, ?)"""
                    cursor.execute(insert_fields, (activity, timeA, listPos))
                    break
                else:
                    messagebox.showwarning("showwarning", "Task order already in use.\nPlease update your order first.")

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

        modSchedScreen.geometry("+{}+{}".format(350, 0))
        modSchedScreen.geometry("700x800")
        modSchedScreen.title("Add new habits")

        def gridSched():
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
                newBookName = simpledialog.askstring("Please enter book name: ", "Book name:")

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
            selectBScreen.geometry("300x300")

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
                        messagebox.showwarning("showwarning", "Please select a book")
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
                        messagebox.showwarning("showwarning", "Please select a book")
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
        bookWindow.geometry("700x750")
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

        bookSummary = Text(bookWindow, wrap=WORD, height=20)
        bookSummary.pack(in_=middle, pady=5, padx=10, expand=TRUE, fill=BOTH)

        lblVocabulary = Label(bookWindow, text="Vocabulary: ")
        lblVocabulary.pack(in_=bottom, side=TOP)

        def notify():
            messagebox.showwarning("Select book", "Please select or add a book first")
            bookName.delete(0, "end")
            bookChapter.delete(0, "end")
            bookSummary.delete(1.0, "end")
            bookVocabulary.delete(1.0, "end")

        butAddVoc = Button(bookWindow, text="Add to Vocabulary", command=notify)
        butAddVoc.pack(in_=bottom, padx=10, pady=5, side=TOP)

        bookVocabulary = Text(bookWindow, wrap=WORD, height=10)
        bookVocabulary.pack(in_=bottom, expand=TRUE, fill=BOTH, pady=5, padx=10)

        def updateBook(currentSel):
            while True:
                id = currentSel[0][0]
                book = bookName.get()
                chapter = bookChapter.get()
                summaryB = bookSummary.get("1.0", 'end-1c')

                vocabulary = bookVocabulary.get("1.0", 'end-1c')
                if book == "":
                    messagebox.showwarning("showwarning", "Please enter a valid book name")
                    break
                if chapter == "" or 50 < int(chapter) < 1:
                    messagebox.showwarning("showwarning", "Please enter a valid chapter")
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
            addVocabScreen.geometry("300x300")

            lblWord = Label(addVocabScreen, text="Add a word to your vocabulary:")
            lblWord.pack(padx=10, pady=5, side=TOP)

            entWord = Entry(addVocabScreen)
            entWord.pack(padx=10, pady=5, side=TOP)

            def addWord():
                enteredWord = entWord.get()
                if enteredWord == "":
                    messagebox.showinfo("No match", "Please enter a word into the text field")
                    return
                while True:
                    meaning = ""
                    try:
                        meaning += f"Noun : {dictionary.meaning(enteredWord)['Noun'][0]} \n"
                    except Exception:
                        pass
                    try:
                        meaning += f"Verb : {dictionary.meaning(enteredWord)['Verb'][0]} \n"
                    except Exception:
                        pass
                    try:
                        meaning += f"Adjective : {dictionary.meaning(enteredWord)['Adjective'][0]} \n"
                    except Exception:
                        try:
                            meaning += f"Adverb : {dictionary.meaning(enteredWord)['Adverb'][0]} \n"
                        except Exception:
                            try:
                                meaning += f"Pronoun : {dictionary.meaning(enteredWord)['Pronoun'][0]} \n"
                            except Exception:
                                try:
                                    meaning += f"Preposition : {dictionary.meaning(enteredWord)['Preposition'][0]} \n"
                                except Exception:
                                    try:
                                        meaning += f"Conjunction : {dictionary.meaning(enteredWord)['Conjunction'][0]} \n"
                                    except Exception:
                                        try:
                                            meaning += f"Interjection : {dictionary.meaning(enteredWord)['Interjection'][0]} \n"
                                        except Exception:
                                            pass
                    if meaning == "":
                        messagebox.showinfo("No match", "Definition for entered word can not be found")
                        break
                    else:
                        bookVocabulary.insert(1.0, f"{enteredWord} - {meaning}\n")
                        entWord.delete(0, 'end')
                        id = currentSel[0][0]
                        vocabulary = bookVocabulary.get("1.0", 'end-1c')

                        sql = "UPDATE Books SET vocabulary = ? WHERE id = ?"

                        cursor.execute(sql, (vocabulary, id,))
                        db.commit()
                    break

            butAdd = Button(addVocabScreen, text="Add Word", command=addWord)
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
            vocScreen.geometry("500x500")

            cursor.execute('SELECT vocabulary FROM books')
            vocabularyArr = cursor.fetchall()

            vocabTxt = Text(vocScreen, wrap=WORD, height=20)
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
                                         "Are you sure you want to return to the main screen? \n \n Unsaved changes will be lost?")
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
        diaryWindow.geometry("700x400")
        top = Frame(diaryWindow)
        top.pack()

        lblDay = Label(diaryWindow, text="Diary entry for: " + now.strftime("%A"), font=("Arial", 14))
        lblDay.pack(in_=top, side=TOP, pady=5)

        lblDate = Label(diaryWindow, text=now.strftime("%d-%B-%Y"), font=("Arial", 20))
        lblDate.pack(in_=top, side=TOP, pady=5)

        lblGrateful = Label(diaryWindow, text="I am grateful for: ")
        lblGrateful.pack(in_=top, side=TOP, padx=5, pady=5)

        gratefulTxt = Text(diaryWindow, wrap=WORD, height=3)
        gratefulTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

        lblPlan = Label(diaryWindow, text="This is how I will make today great: ")
        lblPlan.pack(in_=top, side=TOP, padx=5, pady=5)

        planTxt = Text(diaryWindow, wrap=WORD, height=5)
        planTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

        lblAffirmation = Label(diaryWindow, text="Positive affirmation: ")
        lblAffirmation.pack(in_=top, side=TOP, padx=5, pady=5)

        affirmationTxt = Text(diaryWindow, wrap=WORD, height=2)
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
            selectDScreen.geometry("300x300")

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
                        messagebox.showwarning("showwarning", "Please select a diary")
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
                        messagebox.showwarning("showwarning", "Please select a diary")
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
        diaryWindow.geometry("700x800")
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

        gratefulTxt = Text(diaryWindow, wrap=WORD, height=3)
        gratefulTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

        lblPlan = Label(diaryWindow, text="This is how I will make today great: ")
        lblPlan.pack(in_=top, side=TOP, padx=5, pady=5)

        planTxt = Text(diaryWindow, wrap=WORD, height=5)
        planTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

        lblAffirmation = Label(diaryWindow, text="Positive affirmation: ")
        lblAffirmation.pack(in_=top, side=TOP, padx=5, pady=5)

        affirmationTxt = Text(diaryWindow, wrap=WORD, height=2)
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

        deedTxt = Text(diaryWindow, wrap=WORD, height=2)
        deedTxt.pack(in_=bottom, pady=5, padx=10, expand=TRUE, fill=BOTH)

        lblImprove = Label(diaryWindow, text="How I'll improve: ")
        lblImprove.pack(in_=bottom, side=TOP, padx=5, pady=5)

        improveTxt = Text(diaryWindow, wrap=WORD, height=2)
        improveTxt.pack(in_=bottom, pady=5, padx=10, expand=TRUE, fill=BOTH)

        lblExperiences = Label(diaryWindow, text="Great things I experienced today: ")
        lblExperiences.pack(in_=bottom, side=TOP, padx=5, pady=5)

        experiencesTxt = Text(diaryWindow, wrap=WORD, height=3)
        experiencesTxt.pack(in_=bottom, pady=5, padx=10, expand=TRUE, fill=BOTH)

        def notify():
            messagebox.showwarning("No diary", " You diary is empty, a new entry will now be created")
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
            diaryBookScreen.geometry("500x500")

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
                if diariesArr[dayCounter][2] != "":
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
                if diariesArr[dayCounter][7] != "":
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
                if diariesArr[dayCounter][2] != "":
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
                if diariesArr[dayCounter][7] != "":
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

            diariesTxt = Text(diaryBookScreen, wrap=WORD, height=20)
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
            if diariesArr[dayCounter][2] != "":
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
            if diariesArr[dayCounter][7] != "":
                strDiary += f"\nGreat things I experienced today:\n{diariesArr[dayCounter][7]}"
            diariesTxt.insert(1.0, strDiary)

        butDiaries = Button(diaryWindow, text="Your Diary", font=("Helvetica", 14), command=diariesScreen)
        butDiaries.pack(side=TOP)

        def doneCom():
            option = messagebox.askyesno("Quit",
                                         "Are you sure you want to return to the main screen? \n \n Unsaved changes will be lost?")
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
        goalsWindow.geometry("700x800")
        top = Frame(goalsWindow)
        top.pack()

        lblShort = Label(goalsWindow, text="Short term goals: ", font=("Arial", 14))
        lblShort.pack(in_=top, side=TOP, pady=5)

        shortTxt = Text(goalsWindow, wrap=WORD, height=12)
        shortTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

        lblLong = Label(goalsWindow, text="Long term goals: ", font=("Arial", 14))
        lblLong.pack(in_=top, side=TOP, pady=5)

        longTxt = Text(goalsWindow, wrap=WORD, height=10)
        longTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

        lblNeed = Label(goalsWindow, text="Things I need: ", font=("Arial", 14))
        lblNeed.pack(in_=top, side=TOP, pady=5)

        needTxt = Text(goalsWindow, wrap=WORD, height=8)
        needTxt.pack(in_=top, pady=5, padx=10, expand=TRUE, fill=BOTH)

        lblWant = Label(goalsWindow, text="Things I want: ", font=("Arial", 14))
        lblWant.pack(in_=top, side=TOP, pady=5)

        wantTxt = Text(goalsWindow, wrap=WORD, height=8)
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
                                         "Are you sure you want to return to the main screen? \n \n Unsaved changes will be lost?")
            if option:
                goalsWindow.destroy()

        butDone = Button(goalsWindow, text="Back", font=("Helvetica", 14), command=doneCom)
        butDone.pack(side=TOP, padx=10, pady=10)

        goalsWindow.protocol("WM_DELETE_WINDOW", partial(on_closing, goalsWindow))

    butGoals = Button(topframe, text="Goals", font=("Arial", 10), command=goalScreen)
    butGoals.pack()

    def on_closing(screen):
        if messagebox.askokcancel("Quit", "Are sure you want to quit? \n \n Unsaved changes will be lost."):
            if str(screen) == ".":
                global start_background
                start_background = False
            else:
                screen.destroy()

    window.protocol("WM_DELETE_WINDOW", partial(on_closing, window))



    window.mainloop()

splash_win.after(3000, partial(scheduleScreen, splash_win))
mainloop()
