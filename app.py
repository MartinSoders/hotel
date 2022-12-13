
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
import os
from sqlalchemy.sql import func
from datetime import datetime, timedelta, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://martinso:BANAN123abc456!#@localhost/hotel'
db = SQLAlchemy(app)
migrate = Migrate(app,db)


class Room(db.Model):
    id = db.Column(db.String(5), primary_key=True)
    room_type = db.Column(db.String(7), nullable = False)
    
class Guest(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    phone = db.Column(db.String(30), nullable = False, unique = True)

class Booking(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    room_id = db.Column(db.String(5), db.ForeignKey('room.id'), nullable = False)
    guest_id = db.Column(db.Integer(), db.ForeignKey('guest.id'), nullable = False)
    extra_beds = db.Column(db.Integer(), nullable = False)
    
    ''' Start och slut för besök  '''
    start_date = db.Column(db.Date, nullable = False)
    end_date = db.Column(db.Date, nullable = False)
    
    

class Receipt(db.Model):
    booking_id = db.Column(db.Integer(), db.ForeignKey('booking.id'), nullable = False, primary_key = True)
    ''' När bokningen gjordes '''
    created_time = db.Column(db.DateTime, nullable = False)
    amount = db.Column(db.Float())
    is_payed = db.Column(db.Boolean(), nullable = False)
    
## Lägg till rum från (data/rooms.txt) (för bärbara datorn)
def add_rooms():
    
    with open("data/rooms.txt", "r") as file:
        read_lines = file.readlines()
        for line in read_lines:
            room_id = line[:line.find(";")]
            room_type = line[line.find(";")+1:-1]
            if room_type not in ['enkel','dubbel']:
                print("Något är fel i rumsfilen")
                print(room_type)
            else:
                if not Room.query.filter_by(id=room_id).first():
                    r = Room()
                    r.id = room_id
                    r.room_type = room_type
                    db.session.add(r)
                    db.session.commit()
                    
## Lägg till en gäst
def add_guest():
    g = Guest()      
    os.system("clear")    
    g.first_name = input("Förnamn: ")
    g.last_name = input("Efternamn: ")
    
    phone_string = input("Telefon (0760-123456): ")
    
    
    while not is_phone(phone_string): ### Kontroll att telefonnummer har rätt format 
        print("---- Fel format på telefonnummer ----")
        print(f"Angivet: {g.phone}")
        print("----------Ange igen--------")
        phone_string = input("Telefon (0760-123456): ")
    
    query_phone = Guest.query.filter(Guest.phone.contains(phone_string)).order_by(Guest.id).all()
    if len(query_phone) > 0:
        print(f"Användare finns redan för telefonnummer: {phone_string}")
        print(f"Namn: {query_phone[0].first_name} {query_phone[0].last_name}, Telefon: {query_phone[0].phone}")
        return query_phone[0].phone
        
    
    
    g.phone = phone_string
        
    db.session.add(g)
    db.session.commit()
    input("Klart. Tryck enter för att återgå.")

    return phone_string

## Kollar att det är ett telefonnummer (11 chracters, 1234-0123456)
def is_phone(phone_string):
    if len(phone_string) != 11:
        return False
    for i, letter_i in enumerate(phone_string):
        if i != 4 and letter_i not in "0123456789":
            return False
        if i == 4 and letter_i != "-":          
            return False
    return True

## Tar input och skapar ett datum: ---> date(YYYY,MM,DD)
def input_get_date():
    while True:
        year = "20" + input("År: 20").strip()
        month = input("Månad: ").strip()
        day = input("Dag: ").strip()
        try:
            d = date(int(year), int(month), int(day))
        except:
            input(f"Inget giltig datum: {year}, {month}, {date}. Tryck enter för att fortsätta")
            d = None
        if d:
            return d
        
        



''' Gästens ID '''
## Hittar gäst
def select_guest():
    os.system("clear")
    guest_pick_bool = False
            
    while not guest_pick_bool:
        print("Skriv avslut för att avbryta")
        print("Telefonnummer format 0000-999999")
        phone_nr = input("Skriv / sök telefonummer: ")
        
        if phone_nr == "avslut":            ## Avbryt
            return None
        
        guests = Guest.query.filter(Guest.phone.contains(phone_nr)).order_by(Guest.id).all()
        
        
        if len(guests) == 0:                            ### Hittade ingen med det telefonumret
            print(f"Hittade ingen gäst med telefonnummer: {phone_nr}")
            choice_here = input("Tryck enter för att söka igen. Skriv ny för att lägga till användare")
                    
            if choice_here.lower() == "ny":             ## Om "ny": Skapa ny gäst
                phone_nr = add_guest()
                guests = Guest.query.filter(Guest.phone.contains(phone_nr)).order_by(Guest.id).all()

        if len(guests) == 1:            ### Om ett unikt svar: Godkänt
            guest = guests[0]
            os.system("clear")
            print("---Gäst vald----")
            print(f"Gäst namn: {guest.first_name} {guest.last_name}. \nTelefon: {guest.phone}\n")
            choice_here = input("Tryck enter för att fortsätta. Skriv N för att byta nummer")
            if choice_here.lower() == "n":              ### Om valet är N byt gäst
                os.system("clear")
            else:                                       ### Annars är valet klart
                os.system("clear")
                guest_pick_bool = True   

        if len(guests) > 1:             ### Om flera svar: Visa alla och sök igen
            print("")
            print("---Hittade flera gäster----")
            for g in guests:
                print(g.id, g.first_name, g.last_name, g.phone)
            input("Tryck enter för att söka igen.")   
            print("---------") 
            print("\n\n\n")
    
    return guest.id


### Hämta gäst_id 
def get_guest_id():  
    ### Gästens ID
    while True:
        print("0. Återgå")
        print("1. Ange gästens telefonnummer")
        print("2. Skapa ny gäst")
        selected = input("Välj:")
        
        if selected == "0":                   ### Avbryt
            guest_id == None
            break
        
        elif selected == "1":                 ### Hitta gäst med telefonnummer
            guest_id = select_guest()
            break
        
        elif selected == "2":                 ### Skapa gäst
            phone_str = add_guest()
            guest_id = Guest.query.filter(Guest.phone.contains(phone_str)).first()
            break
        
        else:                                ### Input var inte godkänt. 
            input(f"{selected} är inget giltigt val. Tryck enter och välj igen")    
            os.system("clear")
    
    return guest_id
 
 

def get_start_end_date():
    while True:
        start_date = input_get_date()
        end_date = input_get_date()
        if start_date > end_date:
            break
        else:
            print("Start datum större än slutdatum!")
            print("Försök igen \n\n")
    return start_date, end_date
        

def search_room_between_dates(start_date, end_date):
    if isinstance(start_date, date) and isinstance(end_date, date):
        qry = db.query(Booking).filter(and_(Booking.start_date >= start_date, Booking.end_date <= end_date))
        
        
        
 
## Skapa en bokning
def make_booking():
    
    os.system("clear")
    b = Booking()
    
    ''' Guest ID '''
    guest_id = get_guest_id()
    if not guest_id:                    ### Guest_ID = None ---> Bokning avbruten
            os.system("clear")
            input("Bokning avbruten. Tryck enter för att gå vidare")
    b.guest_id = guest_id 
    
    ''' Datum '''  
    start_date, end_date = get_start_end_date()
    
    
    
        
                  
    print(guest_id)              
    input("Skriv enter för att återgå")




def MakeBooking():
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now()) 
    

if __name__  == "__main__":
    
    
    
    with app.app_context():
        db.create_all()
        add_rooms()
        
        while True:
            print("Vad vill du göra?")
            print("0. Avsluta")
            print("1. Lägg till en ny gäst")
            print("2. Skapa en bokning")


            print("----Helpers------")
            print("20. Visa alla rum")
            print("21. Visa alla gäster")
            
        
            sel = input("Skriv val: ")
            


            
            if sel == "0":                          ### Avslut
                break

            if sel == "1":                          ### Lägg till en gäst
                add_guest()
            
            if sel == "2":                          ### Skapa en bokning
                make_booking()
                           
            if sel == "20":                         ### Visa alla rum
                os.system("clear")
                print("------ALLA RUM--------")
                rooms = Room.query.order_by(Room.id).all()
                for r in rooms:
                   print(r.id, r.room_type)
                print("--------------------")
                input("Tryck enter för att återgå")


            if sel == "21":                         ### Visa alla gäster
                os.system("clear")
                print("------ALLA GÄSTER--------")
                
                for g in Guest.query.order_by(Guest.id).all():
                   print(g.id, g.first_name, g.last_name, g.phone)
                print("--------------------")
                input("Tryck enter för att återgå")













            ### Clear screen
            os.system("clear")
                
               
                
                
    
    
    