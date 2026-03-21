from fastapi import FastAPI, Query, status, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

#                           ----- Data -----
#Q2
doctors = [
    {"id": 1, "name": "Dr. Smith", "specialisation": "Cardiologist", "fee": 200, "experience": 10, "is_available": True},
    {"id": 2, "name": "Dr. Johnson", "specialisation": "Dermatologist", "fee": 150, "experience": 8, "is_available": False},
    {"id": 3, "name": "Dr. Williams", "specialisation": "Pediatrician", "fee": 180, "experience": 12, "is_available": True},
    {"id": 4, "name": "Dr. Brown", "specialisation": "Orthopedic", "fee": 220, "experience": 15, "is_available": True},
    {"id": 5, "name": "Dr. Jones", "specialisation": "Neurologist", "fee": 250, "experience": 20, "is_available": False}, 
    {"id": 6, "name": "Dr. Garcia", "specialisation": "Pediatrician", "fee": 180, "experience": 10, "is_available": True},
    {"id": 7, "name": "Dr. Miller", "specialisation": "Gastroenterologist", "fee": 200, "experience": 12, "is_available": True} 
    ]
#Q4
appointments = []
appt_counter = 1

#                           ----- MODELS -----
#Q6
class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = Field(default="in_person") #describes the type of appointment (in_person, video, emergency)
    senior_citizen: bool = False  #Q9

#Q11
class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialisation: str = Field(..., min_length=2)
    fee: float = Field(..., gt=0, description="Consultation fee")
    experience_years: int = Field(..., gt=0)
    is_available: bool = True

#                           ----- Helper functions -----
#Q7 & Q9
def find_doctor(doctor_id: int):
    return next((d for d in doctors if d["id"] == doctor_id), None)

def calculate_fee(base_fee, appointment_type, senior_citizen):
    if appointment_type not in ["in_person", "video", "emergency"]:
        raise HTTPException(status_code=400, detail="Invalid appointment type")
    if appointment_type == "video":
        fee = base_fee * 0.8  # 80% of the base fee for video consultations
    elif appointment_type == "emergency":
        fee = base_fee * 1.5  # 150% of the base fee for emergency visits
    else:
        fee = base_fee

    original_fee = fee
    if senior_citizen:
        fee *= 0.85 # 15% discount for senior citizens
    return round(base_fee, 2), round(fee, 2)

#Q10
def filter_doctors_logic(specialisation: str = None, max_fee: float = None, min_experience: int = None, is_available: bool = None):
    filtered_doctors = doctors
    if specialisation is not None:
        filtered_doctors = [d for d in filtered_doctors if d["specialisation"].lower() == specialisation.lower()]
    if max_fee is not None:
        filtered_doctors = [d for d in filtered_doctors if d["fee"] <= max_fee]
    if min_experience is not None:
        filtered_doctors = [d for d in filtered_doctors if d["experience"] >= min_experience]
    if is_available is not None:
        filtered_doctors = [d for d in filtered_doctors if d["is_available"] == is_available]
    return filtered_doctors

#                           ----- Root -----
#Q1
@app.get("/")
def read_root():
    return {"message": "Welcome to MediCare Clinic"}

#                           ----- Doctors Routes -----
#Q5
@app.get("/doctors/summary")
def read_doctors_summary():
    total_doctors = len(doctors)
    available_doctors = len([d for d in doctors if d["is_available"]])
    most_experienced_doctor = max(doctors, key=lambda d: d["experience"])
    cheapest_consultation_fee = min(doctors, key=lambda d: d["fee"])["fee"]
    spec_count = {}
    for d in doctors:
        spec_count[d["specialisation"]] = spec_count.get(d["specialisation"], 0) + 1
    
    return {"total_doctors": total_doctors, 
            "available_count": available_doctors, 
            "most_experienced_doctor": most_experienced_doctor["name"], 
            "cheapest_consultation_fee": cheapest_consultation_fee, 
            "count_by_specialisation": spec_count}

#Q2
@app.get("/doctors")
def read_doctors():
    return {"doctors": doctors, 
            "total": len(doctors),
            "available_count": len([d for d in doctors if d["is_available"]])
            }

#Q10
@app.get("/doctors/filter")
def filter_doctors(
    specialisation: Optional[str] = None,
    max_fee: Optional[float] = None, 
    min_experience: Optional[int] = None,
    is_available: Optional[bool] = None ):

    filtered_doctors = filter_doctors_logic(specialisation, max_fee, min_experience, is_available)
    return {"filtered_doctors": filtered_doctors, "count": len(filtered_doctors)}

#Q16
@app.get("/doctors/search")
def search_doctors(keyword: str):
    keyword_lower = keyword.lower()
    matches = [d for d in doctors if keyword_lower in d["name"].lower() or keyword_lower in d["specialisation"].lower()]
    if not matches:
        return {"message": "No doctors found matching the keyword"}
    return {"total_found": len(matches), "matches": matches}

#Q17
@app.get("/doctors/sort")
def sort_doctors(
    sort_by: str ="fee", order: str = "asc" ):
    
    if sort_by not in ["fee", "name", "experience"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    reverse = order == "desc"
    sorted_doctors = sorted(doctors, key=lambda d: d[sort_by], reverse=reverse)
    return {"doctors": sorted_doctors, "sort_metadata": {"sort_by": sort_by, "order": order}}

#Q18 
@app.get("/doctors/page")
def paginate_doctors(
    page: int = 1, limit: int = 3):
    
    total_doctors = len(doctors)
    total_pages = (total_doctors + limit - 1) // limit
    if page > total_pages:
        raise HTTPException(status_code=404, detail="Page not found")
    start = (page - 1) * limit
    end = start + limit
    return {"doctors": doctors[start:end], "pagination": {"current_page": page, "total_pages": total_pages, "limit": limit}}

#Q20
@app.get("/doctors/browse")
def browse_doctors(
    keyword: Optional[str] = None,
    sort_by: str = "fee",
    order: str = "asc",
    page: int = 1,
    limit: int = 4):

    if keyword:
        keyword_lower = keyword.lower()
        filtered_doctors = [d for d in doctors if keyword_lower in d["name"].lower() or keyword_lower in d["specialisation"].lower()]
    else:
        filtered_doctors = doctors

    if sort_by not in ["fee", "name", "experience"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    
    sorted_doctors = sorted(filtered_doctors, key=lambda d: d[sort_by], reverse=(order == "desc"))
    
    total_doctors = len(sorted_doctors)
    total_pages = (total_doctors + limit - 1) // limit
    
    if page > total_pages:
        raise HTTPException(status_code=404, detail="Page not found")
    
    start = (page - 1) * limit
    end = start + limit
   
    return {
        "doctors": sorted_doctors[start:end],
        "metadata": {
            "total_found": total_doctors,
            "sort_by": sort_by,
            "order": order,
            "current_page": page,
            "total_pages": total_pages,
            "page": page,
            "limit": limit
        }
    }

#Q3
@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor
    raise HTTPException(status_code=404, detail="Doctor not found")

#Q11
@app.post("/doctors", status_code=status.HTTP_201_CREATED)  
def add_doctor(new_doctor: NewDoctor):
    if any(d["name"] == new_doctor.name for d in doctors):
        raise HTTPException(status_code=400, detail="Doctor with this name already exists")
    doctor_id = max(d["id"] for d in doctors) + 1 if doctors else 1
    doctor = {
        "id": doctor_id,
        "name": new_doctor.name,
        "specialisation": new_doctor.specialisation,
        "fee": new_doctor.fee,
        "experience": new_doctor.experience_years,
        "is_available": new_doctor.is_available
    }
    doctors.append(doctor)
    return {"message": "Doctor added successfully", "doctor": doctor}

#Q12
@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, fee: Optional[float] = None, is_available: Optional[bool] = None):
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if fee is not None:
        doctor["fee"] = fee
    if is_available is not None:
        doctor["is_available"] = is_available

    return doctor

#Q13
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):  
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if any(a for a in appointments if a["doctor_id"] == doctor_id and a["status"]in ["scheduled", "confirmed"]):
        raise HTTPException(status_code=400, detail="Cannot delete doctor with active appointments")
    doctors.remove(doctor)
    return {"message": "Doctor deleted successfully"}

#                           ----- Appointments Routes -----
#Q4
@app.get("/appointments")
def get_appointments():
    total = len(appointments)
    return {"total_appointments": total, "appointments": appointments}

#Q15
@app.get("/appointments/active")
def get_active_appointments():
    active_appointments = [appt for appt in appointments if appt["status"] in ["scheduled", "confirmed"]]
    return {"appointments": active_appointments}

#Build GET /appointments/by-doctor/{doctor_id} returning all appointments for a specific doctor.
@app.get("/appointments/by-doctor/{doctor_id}")
def get_appointments_by_doctor(doctor_id: int):
    doctor_appointments = [appt for appt in appointments if appt["doctor_id"] == doctor_id]
    return {"appointments": doctor_appointments}

#Q19
@app.get("/appointments/search")
def search_appointments(patient_name: str):
    name_lower = patient_name.lower()
    matches = [a for a in appointments if name_lower in a["patient_name"].lower()]
    if not matches:
        return {"message": "No appointments found for the given patient name"}
    return {"total_found": len(matches), "matches": matches}

#Build GET /appointments/sort — sort by fee or date.
@app.get("/appointments/sort")
def sort_appointments(
    sort_by: str ="date",
    order: str = "asc"):

    if sort_by not in ["final_fee", "date"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    sorted_appointments = sorted(appointments, key=lambda a: a[sort_by], reverse=(order == "desc"))
   
    return {"appointments": sorted_appointments, "sort_metadata": {"sort_by": sort_by, "order": order}}

#Build GET /appointments/page for paginating the appointments list.
@app.get("/appointments/page")
def paginate_appointments(
    page: int = 1,
    limit: int = 3):

    total_appointments = len(appointments)
    total_pages = (total_appointments + limit - 1) // limit

    if total_pages == 0:
        return {"appointments": [], 
                "pagination": {"current_page":1, "total_pages": 0, "limit": limit}
                }
    if page > total_pages:
        raise HTTPException(status_code=404, detail="Page not found")
    start = (page - 1) * limit
    end = start + limit
    
    return {"appointments": appointments[start:end], "pagination": {"current_page": page, "total_pages": total_pages, "limit": limit}}



#Q8
@app.post("/appointments")
def book_appointment(request: AppointmentRequest):
    doctor = find_doctor(request.doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if not doctor["is_available"]:
        raise HTTPException(status_code=400, detail="Doctor is not available")

    original_fee, final_fee = calculate_fee(doctor["fee"], request.appointment_type, request.senior_citizen)
    global appt_counter
    appointment = {
        "appointment_id": appt_counter,
        "patient_name": request.patient_name,
        "doctor_id": request.doctor_id,
        "doctor_name": doctor["name"],
        "appointment_type": request.appointment_type,
        "date": request.date,
        "original_fee": original_fee,
        "final_fee": final_fee,
        "status": "scheduled"
    }
    appointments.append(appointment)
    doctor["is_available"] = False
    appt_counter += 1
    return {"message": "Appointment booked successfully", "appointment": appointment}

#Q14 
@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    appointment = next((a for a in appointments if a["appointment_id"] == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment["status"] != "scheduled":
        raise HTTPException(status_code=400, detail="Only scheduled appointments can be confirmed")
    appointment["status"] = "confirmed"
    return {"message": "Appointment confirmed", "appointment": appointment}

@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    appointment = next((a for a in appointments if a["appointment_id"] == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment["status"] not in ["scheduled", "confirmed"]:
        raise HTTPException(status_code=400, detail="Only scheduled or confirmed appointments can be cancelled")
    appointment["status"] = "cancelled"
    doctor = find_doctor(appointment["doctor_id"])
    if doctor:
        doctor["is_available"] = True
    return {"message": "Appointment cancelled", "appointment": appointment}

#Q15
@app.post("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    appointment = next((a for a in appointments if a["appointment_id"] == appointment_id), None)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment["status"] != "confirmed":
        raise HTTPException(status_code=400, detail="Only confirmed appointments can be completed")
    appointment["status"] = "completed"
    return {"message": "Appointment completed", "appointment": appointment}
