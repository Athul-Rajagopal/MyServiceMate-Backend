# MyServiceMate-Backend

Welcome to the MyserviceMate Backend repository. This repository contains the Beckend code for the Myservicemate project, a worker booking application built with Django-REST-Framework and PostgreSQL for database management.

## Project Overview

Myservicemate is a full-stack project that provides a comprehensive online booking application designed to streamline and simplify household service bookings. The Backend is built using Django-REST-Framework. This README focuses on the backend component of the project.


## Features

### Services Listings by Area
- Browse and explore a wide range of services categorised by area, making it easy to find services available in each area.

### Worker Listing by Area and service
- Listing of workers based on the selected service and area included within a range of 15 kilometers.

### Date and Slot Selection
- Select appointment dates and time slots to book appointments at the user's convenience.

### Online Payment with Stripe
- Make secure online payments for completed works using the Stripe payment gateway, ensuring a seamless and secure transaction process.

### Real-Time Chat with workers
- Engage in real-time chat conversations with workes, improving the overall user experience.


## Installation
1. Clone this repository to your local machine:

   ```shell
   git clone https://github.com/Athul-Rajagopal/MyServiceMate-Frontend.git
   ```

2. Navigate to the project directory
```
cd MyServiceMate
```

3. Create and activate environment
```
python -m venv env
\env\Scripts\activate
```

4. Install the dependecies
```bash
pip install requirements.txt
```

5. Run the backend
```shell
python manage.py runserver
```

