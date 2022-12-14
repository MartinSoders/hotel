
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
import os
from sqlalchemy.sql import func
from sqlalchemy import or_, and_
from datetime import date, datetime, timedelta


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://martinso:BANAN123abc456!#@localhost/hotel'
db = SQLAlchemy(app)
migrate = Migrate(app,db)

''' Klasser -------------------------------------------------------------------------------------------------------------------------------------------------------------------'''

class Room(db.Model):
    id = db.Column(db.String(5), primary_key=True)
    room_type = db.Column(db.String(7), nullable = False)
    extra_beds = db.Column(db.Integer, nullable = False)
    
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
   
   
''' Funktioner -------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
 
''' Dummy funktion som lägger till rum från rooms.txt '''
## Lägg till rum från (data/rooms.txt) (för bärbara datorn)
def add_rooms():
    
    with open("data/rooms.txt", "r") as file:
        read_lines = file.readlines()
        for line in read_lines:
            room_id = line[:line.find(";")]
            chop_string = line[line.find(";")+1:]
            room_type = chop_string[:chop_string.find(";")]
            extra_beds = int(chop_string[chop_string.find(";")+1:-1])

            if room_type not in ['enkel','dubbel']:
                print("Något är fel i rumsfilen")
                print(room_type)
            else:
                if not Room.query.filter_by(id=room_id).first():
                    r = Room()
                    r.id = room_id
                    r.room_type = room_type
                    r.extra_beds = extra_beds
                    db.session.add(r)
                    db.session.commit()
 










        
    
    
        
    
    
    
    
###############################################################################
''' ----------- (Main funks) -------.---------------------------------------'''
###############################################################################
 
''' Skapa en bokning '''
def make_booking():
    
    os.system("clear")
    b = Booking()
    
    ''' Guest ID '''
    guest_id = get_guest_id()
     
    if not guest_id:                    ### Guest_ID = None ---> Bokning avbruten
            os.system("clear")
            input("Bokning avbruten. Tryck enter för att gå vidare")
            del b
            return None
    
    b.guest_id = guest_id
    ''' Datum '''  
    while True:
        ## Ange start och slutdatum
        s_date, e_date = get_start_end_date()
        free_rooms = get_free_rooms(s_date, e_date)
        if len(free_rooms) == 0:
            print("Det finns inga lediga rum mellan datumen")
            sel_here = input("Ange ett annat datum. Eller skriv avslut för att avsluta")
            if sel_here.lower() == "avslut":
                os.system("clear")
                input("Bokning avbruten. Tryck enter för att återgå")
                del b
                return None
            
        else:
            b.start_date = s_date
            b.end_date = e_date
            break
    
    ''' Rum och extrasängar '''
    while True:
        
        # Välj ett ledigt rum
        room = select_room(free_rooms, b)
        
        if not room:   ### Ska bara vara None om man valt avslut
            del b
            return None
        
        # Välj antal extrasängar (för dubbelrum)
        else:          
            b.room_id = room.id
            b.extra_beds = pick_extra_beds(room)
        
        # Loop klar
        os.system("clear")
        break   
    
    
    
    print("Din bokning: \n")
    print(f"Rum ID: {b.room_id}\nGäst ID: {b.guest_id}\nStart Datum: {b.start_date}\nSlut Datum: {b.end_date}\nExtra Sängar:{b.extra_beds}\n")
    sel_here = input("Tryck enter för att godkänna. Skriv avslut för att avbryta")
    
    
    ''' Lägg till bokning i databas (med kontroll så alla fält har värden)'''
    
    if sel_here.lower() == "avslut":  ## Om avslut (lägger ej till)
        return None
      
    else:                              ## Lägger till i databas
        booking_test = booking_has_values(b)
        if booking_test:    # Om alla fält har värden, commit till databas
            db.session.add(b)
            db.session.commit()
          
        else:    # Felmeddelande om någon kolumn saknar värden. (Ska inte häda)
            del b  
            return None
    
        
    ''' Skapa ett kvitto '''
    r = make_reciept(b)
    db.session.add(r)
    db.session.commit()
    
    
    
    os.system("clear")
    print("----- Ditt kvitto-------")
    print(f"Kvitto ID: {r.booking_id}\nBetalad: {r.is_payed},\nBelopp:{r.amount},\nSkapad datum:{r.created_time}\n")
    input("Tryck enter för att fortsätta")
    
    return True

''' Ändra en gäst ''' 
def edit_guest():
    
    ## Kolla att nummret är godkänt
    phone_bool = False
    while True:
        
        phone_string = input('Ange telefon-nummer:')
        if is_phone(phone_string):
            break
        
        else:
            input("Ange godkänt telefonnummer (enter för att fortsätta)")
            os.system("clear")
        
                
    
    ## Sök efter telefonnummer 
    get_qry = db.session.query(Guest).filter_by(phone=phone_string).all()
    
    
    if get_qry != []:
        qry = get_qry[0]
        print(f"Nuvarande namn: {qry.first_name} {qry.last_name}")
        qry.first_name = input(f"Skriv nytt förnamn: ")
        qry.last_name = input(f"Skriv nytt efternamn: ")
        db.session.commit()
        
        
    
    else:
        input("Finns ingen gäst med detta telefon-nummer. Enter för att återgå")
        return None
      

def delete_guest():
    
    ## Kolla att nummret är godkänt
    phone_bool = False
    while True:
        
        phone_string = input('Ange telefon-nummer:')
        if is_phone(phone_string):
            break
        
        else:
            input("Ange godkänt telefonnummer (enter för att fortsätta)")
            os.system("clear")
        
                
    
    
    ## Sök efter telefonnummer 
    get_qry = db.session.query(Guest).filter_by(phone=phone_string).all()

    if get_qry != []:
        qry = get_qry[0]
        if guest_has_bookings(qry):
            print("Kunden har framtida bokningar, kan inte tas bort!")
            input("----Tryck enter för att återgå ---------------")
            
        else:
            while True:
                print("Kunden har inga framtida bokningar och kan tas bort!")
                print(f"Vill du ta bort: {qry.first_name} {qry.last_name} \nMed Telefon: {qry.phone}")
                del_sel = input("Y/N: ")
                if del_sel.lower() == "y":
                    db.session.delete(qry)
                    db.session.commit()
                    return True
                elif del_sel.lower() == "n":
                    return None

                else:
                    print("------FEL INPUT------------------\nVälj Y/N \n")
                
    else:
        input("Finns ingen kund med det nummret (enter för att återgå)")    
        return None
    
def edit_booking():
    os.system('clear')
    phone_str = input("Skriv gästens telefon-nummer")
    
    ## Kolla om gäst finns
    get_qry = db.session.query(Guest).filter_by(phone=phone_str).all()    
    if get_qry == []:
        input("Finns ingen gäst med det telefonnummer (enter för att återgå)")
        return None
    else:
        guest_id = get_qry[0].id

    ## Visa bokningar
    get_qry = db.session.query(Booking).filter_by(guest_id=guest_id).all()   
    
    if get_qry == []:
        input("Gäst har inga bokningar telefonnummer (enter för att återgå)")
        return None
    
    else:
        print("---Bokningar för gäst")
        booking_dict = {}
        for q in get_qry:
            booking_dict[str(q.id)] = q
            print(f"Boknings-id: {q.id}, Rum: {q.room_id}, Datum: {q.start_date} - {q.end_date}")
        
        book_id = input("Välj boknings-id: ")
        if book_id in booking_dict.keys():
            booking = booking_dict[book_id]
        else:
            input("Finns ingen bokning med det ID:t (enter för att återgå)")
            return None
        
    get_qry = db.session.query(Booking).filter_by(room_id=booking.room_id).all()   
    min_date = datetime.now().date() + timedelta(days=1)
    max_date = booking.end_date + timedelta(days=30)

    for room_booking in get_qry:
        
        ### Om slutdatum    
        if room_booking.id != booking.id:
            
            ## Om start ligger mellan min-max 
            if room_booking.start_date <= max_date and room_booking.end_date >= min_date:
            
            
                ## Om bokningen ligger före 
                if room_booking.start_date <= booking.start_date:
                    min_date = room_booking.end_date
                
                ## Om bokningen ligger efter:
                if room_booking.start_date >= booking.end_date:
                    max_date = room_booking.start_date

    
    print("--------------------------------------------------------")
    print(f"Ange nytt startdatum, rummet är ledig från: {min_date}")
    start_date = input_get_date()
    if start_date < min_date:
        input("För tidigt datum, var god försök igen (enter)")
        return None
    
    print("--------------------------------------------------------")   
    print(f"Ange nytt slutdatum, rummet är ledig tills: {max_date}")
    stop_date = input_get_date()
    if stop_date > max_date:
        input("För högt datum, var god försök igen (enter)")
        return None
        
    if start_date > stop_date:
        input("Start datum måste vara lägre än slut datum")
        return None
        
    room = db.session.query(Room).filter_by(id=booking.room_id).one()
    booking.extra_beds = pick_extra_beds(room)
    
    
    booking.start_date = start_date
    booking.end_date = stop_date
    db.session.commit()
    os.system("clear")
    print("Updaterat!")
    print(f"Rum ID: {booking.room_id}")
    print(f"Datum: {booking.start_date} - {booking.end_date}")
    print(f"Extra-sängar: {booking.extra_beds}")
    input("Tryck enter för att återgå")
    return True



def delete_booking():
    os.system('clear')
    phone_str = input("Skriv gästens telefon-nummer")
    
    ## Kolla om gäst finns
    get_qry = db.session.query(Guest).filter_by(phone=phone_str).all()    
    if get_qry == []:
        input("Finns ingen gäst med det telefonnummer (enter för att återgå)")
        return None
    else:
        guest_id = get_qry[0].id

    ## Visa bokningar
    get_qry = db.session.query(Booking).filter_by(guest_id=guest_id).all()   
    
    if get_qry == []:
        input("Gäst har inga bokningar telefonnummer (enter för att återgå)")
        return None
    
    else:
        print("---Bokningar för gäst")
        booking_dict = {}
        for q in get_qry:
            booking_dict[str(q.id)] = q
            print(f"Boknings-id: {q.id}, Rum: {q.room_id}, Datum: {q.start_date} - {q.start_date}")
        
        book_id = input("Välj boknings-id: ")
        if book_id in booking_dict.keys():
            booking = booking_dict[book_id]
        else:
            input("Finns ingen bokning med det ID:t (enter för att återgå)")
            return None
    
    print(f"Vill du ta bort bokningen mellan {booking.start_date} - {booking.end_date}??")
    while True:
        delete_sel = input("[Y/N]: ")
        if delete_sel.lower() == "y":
            reciept = db.session.query(Receipt).filter_by(booking_id=booking.id).one()
            db.session.delete(reciept)
            db.session.commit()
            db.session.delete(booking)
            db.session.commit()
            return True
        elif delete_sel.lower() == "n":
            return None
        
 
###############################################################################
''' ----------- GÄST: Välja / Skapa / Söka ---------------------------------'''
###############################################################################

                   
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
    if len(query_phone) == 1:
        print(f"Användare finns redan för telefonnummer: {phone_string}")
        print(f"Namn: {query_phone[0].first_name} {query_phone[0].last_name}, Telefon: {query_phone[0].phone}")
        input("---------------------------------")
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
            return None
        
        elif selected == "1":                 ### Hitta gäst med telefonnummer
            guest_id = select_guest()
            break
        
        elif selected == "2":                 ### Skapa gäst
            phone_str = add_guest()
            guest = Guest.query.filter(Guest.phone.contains(phone_str)).first()
            guest_id = guest.id
            break
        
        else:                                ### Input var inte godkänt. 
            input(f"{selected} är inget giltigt val. Tryck enter och välj igen")    
            os.system("clear")
    
    return guest_id
 
 
### Om kund har bokningar
def guest_has_bookings(guest_object):
    ## Sök efter telefonnummer 
    qry = db.session.query(Booking).filter_by(guest_id=guest_object.id).all()
    for booking in qry:
        if booking.start_date >= datetime.now().date():
            return True
    return False
        
    
    
###############################################################################
''' ----------- RUM OCH DATUM ------------ ---------------------------------'''
###############################################################################

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
 
''' Start och slutdatum '''
def get_start_end_date():
    while True:
        os.system("clear")
        print("Skriv start datum")
        start_date = input_get_date()
        if start_date < datetime.now().date():
            print("Bokning måste ske efter dagens datum")
            input("tryck enter för att gå vidare")   
               
        
        else:
            os.system("clear")
            print(f"Från: {start_date}\n")
            break
        
    while True:
        print("Skriv slut datum")
        end_date = input_get_date()
        
        if start_date > end_date:
            print("Slut-datum är före start-datum!")
            print("Försök igen \n\n")
            input("tryck enter för att gå vidare") 
            os.system("clear")
        
        else:
            return start_date, end_date

## Hitta alla bokade rum              
def get_booked_rooms(start_date: date, end_date: date):
    if isinstance(start_date, date) and isinstance(end_date, date):
        qry = db.session.query(Booking).filter(and_(Booking.end_date >= start_date, Booking.start_date <= end_date))
        booked_rooms = list(set([q.room_id for q in qry.all()]))
    return booked_rooms
        
## Hitta alla lediga rum    
def get_free_rooms(start_date, end_date):
    if isinstance(start_date, date) and isinstance(end_date, date):      
        ## Hämta alla bokade rum
        reserved_list = get_booked_rooms(start_date, end_date)
        
        ## Lägg till dem som inte är bokade
        not_reserved = []
        for r in db.session.query(Room).distinct(Room.id):
            if r.id not in reserved_list:
                not_reserved.append(r)
                
        return not_reserved
        
## Välj ett rum från listan med lediga        
def select_room(room_list, booking):    
    try:
        
        while True:
            os.system("clear")
            print("----------------")
            print(f'Datum: {booking.start_date} - {booking.end_date}')
            print("Lediga rum \n")
            
            ## Visa alla rum på listan
            for r in room_list:
                print('Rum ID: ',r.id, '    Typ:', r.room_type, ' rum')
            print("----------------")
            
            
            ## Välj rum från listan
            sel_room = input("Välj ett rum id: ")
            for r in room_list:
                if sel_room == r.id:
                    return r

            ### Hit kommer man bara om rummet inte finns
            print("Skriv avslut för att avsluta")
            end_sel = input(f"Finns inget rum med ID: {sel_room}. Tryck enter och välj ett annat rum")
        
            ## Return none och avsluta
            if end_sel.lower() == "avslut":
                return None
        
    except:
        print("Något gick helt fel")
        input("---- Tryck enter för att avsluta")
        raise  RuntimeError


def get_rooms_for_people():
    
    try:
        guest_number = int(input("Skriv in antal gäster :"))    
    except:
        input("Inte en giltig siffra (Enter för att återgå)")        
        return None
    
    start_date = input_get_date()
    stop_date = input_get_date()
    
    free_room_list = get_free_rooms(start_date, stop_date)
    
    rooms_for_guests = []
    for room_x in free_room_list:
        if room_x.room_type == "enkel":
            max_guests = 1
        if room_x.room_type == "dubbel":
            max_guests = 2 + room_x.extra_beds
        if guest_number <= max_guests:
            rooms_for_guests.append(room_x)
    
    os.system("clear")
    if rooms_for_guests == []:
        print(f'Det fanns inga rum för {guest_number} mellan {start_date} och {stop_date}')
        input("Tryck enter för att gå vidare")
        return None
    else:
        print(f"Lediga rum för {guest_number} mellan {start_date} och {stop_date}")
        for room_x in rooms_for_guests:
            print(f"ID: {room_x.id}, Typ: {room_x.room_type}, Extra-sängar: {room_x.extra_beds}")
        input("Tryck enter för att gå vidare")
        return True
            
        
            
        
    
    

###############################################################################
''' ----------- Extrasängar och kontroll - ---------------------------------'''
###############################################################################

    
''' Extrasängar '''     
def pick_extra_beds(room_obj):
    if room_obj.extra_beds == 0:
        return 0
    
    while True:
        os.system("clear")
        sel_beds = input(f"Välj antal extrasängar (0- {room_obj.extra_beds}): ")
        try:
            sel_int = int(sel_beds)
            is_int = False
            
        except:
            print("Skriv en giltig siffra")
            input("---Tryck enter för att gå tillbaks")
            sel_int = None
        
        if isinstance(sel_int, int):
            if sel_int >= 0 and sel_int <= room_obj.extra_beds:
                return sel_int

            else:
                print(f"Välj en siffra mellan 0 och {room_obj.extra_beds} inte {sel_int}")
                input("---Tryck enter för att gå tillbaks") 


''' Kontrollera att alla fält har värden'''            
## Check that all fields have values! 
def booking_has_values(bk):
    for f in [bk.room_id, bk.guest_id, bk.start_date, bk.end_date, bk.extra_beds]:
        if f == None:
            print("Något gick fel, bokningen avbruten!")
            print(bk.room_id, bk.guest_id, bk.start_date, bk.end_date, bk.extra_beds)
            input("--------Enter för att återgå -----------")
            return False
        
    return True



###############################################################################
''' ----------- Kvitto ------------------- ---------------------------------'''
###############################################################################


''' Beräkna (dummy) pris '''
def set_dummy_price(bk):
    
    room = db.session.query(Room).filter(Room.id == bk.room_id).first()
    if room.room_type == "enkel":
        day_price = 500
        
    if room.room_type == "dubbel":
        day_price = 900 + 300 * bk.extra_beds
    
    delta = (bk.end_date - bk.start_date).days + 1
    
    return delta * day_price
     
''' Skapa ett kvitto '''       
def make_reciept(bk):
    re = Receipt()
    re.booking_id = bk.id
    re.created_time = datetime.now()
    re.amount = set_dummy_price(bk)
    re.is_payed = False
    return re
      

def check_reciept():
    qry = db.session.query(Receipt).filter(Receipt.is_payed == False).all()
    
    deletes = []
    
    for this_reciept in qry:
        delta = datetime.now() - this_reciept.created_time
        if delta.days >= 11:
            this_booking = db.session.query(Booking).filter(Booking.id == this_reciept.booking_id).one()
            print(f"Mer än 10 dagar gammalt: Boknings ID: {this_reciept.booking_id} Betal status: {this_reciept.is_payed} Skapad: {this_reciept.created_time}, Rum: {this_booking.room_id}")
            
            db.session.delete(this_reciept)
            db.session.commit()
            db.session.delete(this_booking)
            db.session.commit()
    input("Klart: Tryck enter för att återgå")
    return True

        
        
        
        
        
    


        
      
    
    



if __name__  == "__main__":
    
    
    
    with app.app_context():
        db.create_all()

        
        while True:
            print("Vad vill du göra?")
            print("0. Avsluta")
            print("1. Skapa en bokning")   
            print("2. Ändra en kund")         
            print("3. Ta bort en kund")
            print("4. Ändra bokning")
            print("5. Ta bort bokning")
            print("6. Radera bokningar som inte är betalada")
            print("7. Sök ledigt rum för X personer")
            
            print("\n----Helpers------")
            print("20. Visa alla rum")
            print("21. Visa alla gäster")
            print("22. Lägg till en ny gäst")
            print("23. Visa alla bokningar")
            
            sel = input("Skriv val: ")
            


            
            if sel == "0":                          ### Avslut
                break


                
            
            if sel == "1":                          ### Skapa en bokning
                status_value = make_booking()
                
                
            if sel == "2":                          ### Ändra gäst
                status_value = edit_guest()
                     
                     
            if sel == "3":                          ### Ta bort gäst
                status_value = delete_guest()           
            
            if sel == "4":                          ### Ändra en bokning
                status_value = edit_booking()
            
            if sel == "5":
                status_value = delete_booking()     ### Radera bokning
            
            if sel == "6":
                status_value = check_reciept()      ### Radera bokning
                
            if sel == "7":                          ### Sök rum för X personer      
                status_values = get_rooms_for_people()
                
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

            if sel == "22":                          ### Lägg till en gäst
                status_value = add_guest()


            if sel == "23":                         ### Visa alla gäster
                os.system("clear")
                print("------ALLA GÄSTER--------")
                
                for b in Booking.query.order_by(Booking.room_id, Booking.start_date).all():
                   print(b.room_id, b.start_date, b.end_date)
                print("--------------------")
                input("Tryck enter för att återgå")








            ### Clear screen
            os.system("clear")
                
               
                
                
    
    
    