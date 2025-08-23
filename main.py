import db
from gui import App

if __name__=="__main__":
    db.create_tables() # инициализация БД
    app=App()
    app.mainloop()

