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


window = Tk()

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
#cursor.execute("INSERT INTO activities(activity, timeA, listPos) VALUES (Task, 0, 0)")

def doneScreen():
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
    scheduleScreen()

# Center
def scheduleScreen():
    global stop_background
    stop_background = False
    for widget in window.winfo_children():
        widget.destroy()

    window.geometry("+{}+{}".format(500, 200))
    window.geometry("500x500")
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
            timeN = datetime.now().strftime("%H:%M:%S")
            lblTime.config(text=timeN)
            time.sleep(1)

            if stop_background:
                break

    b = threading.Thread(name='background', target=background, daemon=True)
    b.start()

    #lbl5 = Label(topframe, text=start, font=("Arial", 30))
    #lbl5.pack()

    lblAct = Label(topframe, text="", font=("Arial", 40))
    lblAct.pack(pady=15)

    lblTimeA = Label(topframe, text="", font=("Arial", 20))
    lblTimeA.pack(pady=10)

    def next():
        try:
            activity = activities.pop(0)
            lblAct.config(text=activity)
            lblAct.pack()

            aTime = minutes.pop(0)
            alarm_time = datetime.now() + timedelta(minutes=aTime)
            alarm_time = alarm_time.strftime("%H:%M:%S")
            lblTimeA.config(text=alarm_time)

        except Exception as e:
            lblAct.config(text="Good work, tasks completed." + "\n" + "Please update your schedule for tomorrow." +
                               "\n" + "Stay Hard!", font=("Arial", 14))
            alarm_time = datetime.now()
            alarm_time = alarm_time.strftime("%H:%M:%S")
            lblTimeA.config(text=alarm_time)
            butNext.destroy()
            butSched.config(text="Set schedule for tomorrow", font=("Arial", 20))
            pass

        '''if activity == "Breathing":
            global driver
            driver = webdriver.Chrome(service=s)
            driver.get("https://www.youtube.com/watch?v=tybOi4hjZFQ")
        if activity == "Work for an hour":
            driver.quit()
            pass
        '''

    butNext = Button(topframe, text="Next Habit", command=next, font=("Arial", 20))
    butNext.pack()


    butSched = Button(topframe, text="Schedule your day", font=("Arial", 10), command=modSchedule)
    butSched.pack(pady=50)

    butBook = Button(topframe, text="Books", font=("Arial", 10) , command=bookScreen)
    butBook.pack()

def modSchedule():
    '''def popUp(text):
        userInput = simpledialog.askstring("Please enter new: ", text)
        return userInput'''

    def addActivity():
        txtActivity = "Activity"
        txtTime = "Time(Min) for activity"
        textOrder = "Order of activity"

        while True:
            activity = simpledialog.askstring("Please enter new: ", txtActivity)
            if activity == None:
                break
            if activity == "":
                messagebox.showwarning("showwarning", "Please enter a valid activity")
                continue
            timeA = simpledialog.askinteger("Please enter new: ", txtTime)
            if timeA == None:
                break
            listPos = simpledialog.askinteger("Please enter new: ", textOrder)
            if listPos == None:
                break
            if listPos < 1:
                messagebox.showwarning("showwarning", "Please enter a valid task order")
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
                messagebox.showwarning("showwarning", "Task order already in use")


        db.commit()
        modSchedule()

        #activities.append(txtN.get())
        #minutes.append(30)

    def removeEntry(input):
        cursor.execute('SELECT activity FROM activities WHERE id = ?', (input,))
        activity = str(cursor.fetchall())
        pattern = r'[^A-Za-z0-9]+'
        # Remove special characters from the string
        act = re.sub(pattern, '', activity)

        if messagebox.askyesno("Deleting Entry", f"Are you sure you want to delete task: {act}"):
            sql = "DELETE FROM activities WHERE id = ?"

            cursor.execute(sql, (input,))

            db.commit()

        modSchedule()

    def updateEntry(input):

        actV = "Activity"
        timeV = "Time(Min) for activity"
        rowV = "Order of activity"

        while True:
            activity = simpledialog.askstring("Please enter new: ", actV)
            if activity == None:
                break
            if activity == "":
                messagebox.showwarning("showwarning", "Please enter a valid activity")
                continue
            timeA = simpledialog.askinteger("Please enter new: ", timeV)
            if timeA == None:
                break
            listPos = simpledialog.askinteger("Please enter new: ", rowV)
            if listPos == None:
                break
            if listPos < 1:
                messagebox.showwarning("showwarning", "Please enter a valid task order")
                continue

            sql = "UPDATE activities SET activity =?, timeA =?, listPos = ? WHERE id = ?"

            cursor.execute(sql, (activity, timeA, listPos, input,))
            break

        db.commit()
        modSchedule()


    global stop_background
    stop_background = True
    for widget in window.winfo_children():
        widget.destroy()

    window.geometry("+{}+{}".format(350, 0))
    window.geometry("700x800")
    window.title("Add new habits")

    #lbl = Label(window, text="Your daily schedule")
    #lbl.grid(column=1)

    btn = Button(window, text="Add new activity +", command=addActivity)
    btn.grid(column=1, row=1, pady=10)

    btn = Button(window, text="Back", command=doneScreen)
    btn.grid(column=4, row=1)

    lbl = Label(window, text="Order")
    lbl.grid(column=0, row=2, padx=30)

    lbl = Label(window, text="Activity")
    lbl.grid(column=1, row=2, padx=80)

    lbl = Label(window, text="Time(Min)")
    lbl.grid(column=2, row=2, padx=40)

    cursor.execute("SELECT * FROM activities")
    if cursor.fetchall() != None:
        x =0
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
                for widget in window.winfo_children():
                    widget.config(font=("Arial", iFont))
                iFont -= 1

            lblOne = Label(window, text=arrayNew[x][3], font=("Arial", 14))
            lblOne.grid(column=0, row=x + 3)

            lblOne = Label(window, text=arrayNew[x][1])
            lblOne.grid(column=1, row=x + 3)

            lblOne = Label(window, text=arrayNew[x][2])
            lblOne.grid(column=2, row=x + 3)

            btn = Button(window, text="Delete", command=partial(removeEntry, arrayNew[x][0]), font=("Arial", 14))
            btn.grid(column=3, row=x + 3, pady=10, padx=10)

            btn = Button(window, text="Update", command=partial(updateEntry, arrayNew[x][0]))
            btn.grid(column=4, row=x + 3, pady=10)

            x += 1

            cursor.execute("SELECT * FROM activities")
            if len(arrayNew) <= x:
                break


def bookScreen():

    for widget in window.winfo_children():
        print(widget)
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

    cursor.execute('SELECT * FROM books WHERE id = 1')
    currentSel = cursor.fetchall()

    def addBook():
        while True:
            newBookName = simpledialog.askstring("Please enter book name: ", "Book name:")

            if newBookName == None:
                break
            if newBookName == "":
                messagebox.showwarning("showwarning", "Please enter a valid activity")
                continue
            cursor.execute("INSERT INTO Books(book, chapter, summary, vocabulary) VALUES (?, ?, ?, ?)", (newBookName, 1, "Chapter 1:\n\n================", ""))
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

    def selectBook():
        cursor.execute('SELECT id, book FROM Books')
        booksArr = cursor.fetchall()
        if booksArr == []:
            messagebox.showwarning("No book", "Please add a new book first.")
            return

        selectBScreen = Toplevel(bookWindow)
        selectBScreen.title("Select Book")
        selectBScreen.geometry("300x300")

        pattern = r'[^A-Za-z0-9]+'
        print(booksArr)
        books = []
        bookIdList = []
        for i in range(0, len(booksArr)):
            book = re.sub(pattern, '', str(booksArr[i][1]))
            bookIdList.append(booksArr[i][0])
            books.append(book)
        scrollBar = Scrollbar(selectBScreen, bg="grey")
        print(bookIdList)

        scrollBar.pack(side=RIGHT, fill=BOTH)
        bookList = Listbox(selectBScreen, selectmode=BROWSE,  yscrollcommand=scrollBar.set)
        scrollBar.config(command=bookList.yview)
        bookList.pack(fill=BOTH, pady=10, padx=10)

        for i in range(0, len(books)):
            bookList.insert(i, books[i])

        def selectedBook():
            while True:
                if bookList.curselection() == ():
                    break
                pattern = r'[^A-Za-z0-9]+'
                choice = re.sub(pattern, '', str(bookList.curselection()))
                choice = bookIdList[int(choice)]
                print(choice)
                if choice == ():
                    messagebox.showwarning("showwarning", "Please select a book")
                    break
                cursor.execute('SELECT * FROM books WHERE id = ?', (choice, ))
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
                pattern = r'[^A-Za-z0-9]+'
                choice = re.sub(pattern, '', str(bookList.curselection()))
                choice = bookIdList[int(choice)]
                print(choice)
                if choice == ():
                    messagebox.showwarning("showwarning", "Please select a book")
                    break
                print(choice)
                cursor.execute('SELECT book FROM Books WHERE id = ?', (choice, ))
                book = str(cursor.fetchall())
                print(book)
                pattern = r'[^A-Za-z0-9]+'
                # Remove special characters from the string
                bookS = re.sub(pattern, '', book)

                if messagebox.askyesno("Deleting Entry", f"Are you sure you want to delete book: {bookS}"):
                    sql = "DELETE FROM Books WHERE id = ?"

                    cursor.execute(sql, (choice, ))
                    db.commit()

                    bookList.delete(choice)
                    selectBScreen.destroy()
                    bookName.delete(0, "end")
                    bookChapter.delete(0, "end")
                    bookSummary.delete(1.0, "end")
                    bookVocabulary.delete(1.0, "end")
                    butSave.config(command=notify)
                break

        butDeleteBook = Button(selectBScreen, text="Delete Book", command=removeBook)
        butDeleteBook.pack()

    bookWindow = Toplevel(window)
    bookWindow.title("Your Books")
    bookWindow.geometry("700x750")
    top = Frame(bookWindow)
    top.pack()

    middle = Frame(bookWindow, width=500, height=100)
    middle.pack()

    bottom = Frame(bookWindow,  width=500, height=100)
    bottom.pack()

    addBook = Button(bookWindow, text="Add new book", command=addBook)
    addBook.pack(in_ = top, side=TOP, pady=5)

    selectBook = Button(bookWindow, text="Select book", command=selectBook)
    selectBook.pack(in_=top, side=TOP, pady=5)

    lblName = Label(bookWindow, text="Name: ")
    lblName.pack(in_ = top, side=LEFT, padx=5, pady=5)

    bookName = Entry(bookWindow)
    bookName.pack(in_ = top, side=LEFT)

    lblChapter = Label(bookWindow, text="Chapters: ")
    lblChapter.pack(in_ = top, side=LEFT, padx=5, pady=5)

    bookChapter = Entry(bookWindow)
    bookChapter.pack(in_ = top, side=LEFT)

    lblSummary = Label(middle, text="Summary: ")
    lblSummary.pack(in_ = middle)

    bookSummary = Text(bookWindow,  wrap=WORD, height=20)
    bookSummary.pack(in_ = middle, pady=5, padx= 10, expand=TRUE, fill=BOTH)

    lblVocabulary = Label(bookWindow, text="Vocabulary: ")
    lblVocabulary.pack(in_ = bottom, side=TOP)

    def notify():
        messagebox.showwarning("Select book", "Please select or add a book first")
        bookName.delete(0, "end")
        bookChapter.delete(0, "end")
        bookSummary.delete(1.0, "end")
        bookVocabulary.delete(1.0, "end")

    butAddVoc = Button(bookWindow, text="Add to Vocabulary", command=notify)
    butAddVoc.pack(in_ = bottom, padx=10, pady=5, side=TOP)

    bookVocabulary = Text(bookWindow, wrap= WORD , height=10)
    bookVocabulary.pack(in_ = bottom, expand=TRUE, fill=BOTH, pady=5, padx= 10)

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
            if chapter == "" or int(chapter) < 1:
                messagebox.showwarning("showwarning", "Please enter a valid chapter")
                break
            if summaryB == "":
                messagebox.showwarning("showwarning", "Please enter summary for the chapter")
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

        addVocabScreen = Toplevel(bookWindow)
        addVocabScreen.title("Add a word to your vocabulary")
        addVocabScreen.geometry("300x300")

        lblWord = Label(addVocabScreen, text="Add a word to your vocabulary:")
        lblWord.pack(padx=10, pady=5, side=TOP)

        entWord = Entry(addVocabScreen)
        entWord.pack(padx=10, pady=5, side=TOP)

        def addWord():
            enteredWord = entWord.get()
            print(enteredWord)
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
                bookVocabulary.insert(1.0, f"{enteredWord} - {meaning}\n")
                entWord.delete(0, 'end')
                break

        butAdd = Button(addVocabScreen, text="Add Word", command=addWord)
        butAdd.pack(padx=10, pady=5, side=TOP)

        def desVoc():
            addVocabScreen.destroy()

        butDone = Button(addVocabScreen, text="Back", command=desVoc)
        butDone.pack(padx=10, pady=5, side=TOP)

    def vocabScreen():
        vocScreen = Toplevel(bookWindow)
        vocScreen.title("List of words in vocabulary")
        vocScreen.geometry("500x500")

        cursor.execute('SELECT vocabulary FROM books')
        vocabularyArr = cursor.fetchall()

        vocabTxt = Text(vocScreen,  wrap=WORD, height=20)
        vocabTxt.pack(pady=5, padx= 10, expand=TRUE, fill=BOTH)

        vocabTxt.delete(1.0, "end")

        for i in range(0, len(vocabularyArr)):
            strWord = str(vocabularyArr[i][0])

            vocabTxt.insert(1.0, f"{strWord}")

    butBook = Button(bookWindow, text="Your Vocabulary", font=("Helvetica", 14), command=vocabScreen)
    butBook.pack(side=TOP)

    def doneCom():
        option = messagebox.askyesno("Quit", "Are you sure you want to return to the main screen? \n \n Unsaved changes will be lost?")
        if option:
            bookWindow.destroy()


    butDone = Button(bookWindow, text="Back", font=("Helvetica", 14), command=doneCom)
    butDone.pack(side=TOP, padx=10, pady=10)

    bookWindow.protocol("WM_DELETE_WINDOW", partial(on_closing, bookWindow))

def on_closing(screen):
    if messagebox.askokcancel("Quit", "Are sure you want to quit? \n \n Unsaved changes will be lost."):
        screen.destroy()

window.protocol("WM_DELETE_WINDOW", partial(on_closing, window))

m = threading.Thread(name='main', target=doneScreen())

m.start()
dictionary = PyDictionary
window.mainloop()

# TODO: Quote of the day... (api)
# TODO: Make stock day schedule?
# TODO: https://www.youtube.com/watch?v=gVKEM4K8J8A&ab_channel=StardustVibes-RelaxingSounds for styding
# TODO: Turn to exe`

#  Button organise schedule > new screen
#  Button finish schedule > return to screen
# Organise screen: show schedule  - {dictionary.meaning(words[y])
