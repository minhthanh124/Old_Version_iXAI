# VisX.AI App

## Project Overview
The **VisX.AI App** is designed to help users perform the AI model explanation using open-source XAI techniques. It provides a user-friendly interface that eliminates the need for programming, effectively lowering technical barriers to visualizing model explanations. This empowers both technical and non-technical users to easily apply open-source XAI techniques. Users simply upload their data, select the modality and task, and immediately receive visualized explanation results, without the need for any complex configuration.

The application features a **Django** back-end and a **React (Next.js)** front-end, with **PostGreSQL** as the database, **MinIO** as object storage and **Docker** as deployment.

## Project Structure
- **Back-end**: Django (Python)
- **Front-end**: Next.js (React framework)
- **Database**: PostGreSQL
- **Object Storage**: MinIO
- **Deployment**: Docker

## Features
- Modality and Task Selection.
- Data Uploading
- Explanation results visualization.

## Prerequisites
Ensure you have the following installed on your system:

- **Python 3.12 or higher**
- **Node.js 14.x or higher** and **npm** (or **Yarn**)
- **Git**
- **Docker**

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/minhthanh124/VisX.AI_Application.git
```

### 2. Set Up the Back-end (Django)

#### a. Create a Virtual Environment

- **Windows**:

  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

- **macOS/Linux**:

  ```bash
  python -m venv venv
  source venv/Scripts/activate
  ```

#### b. Install Dependencies

```bash
cd VisX.AI_Application/
pip install -r requirements.txt
```
### 3. Set Up the Front-end (Next.js)

Navigate to the `frontend` directory and install dependencies:

```bash
cd frontend/visxai_app/

npm install -D tailwindcss postcss autoprefixer
npm install -D postcss postcss-cli
npx @tailwindcss/cli
npx tailwindcss init -p
npm install zustand
npx create-next-app@latest visxai_app --typescript
npm install --save-dev typescript @types/react @types/react-dom
npm install -D typescript @types/react @types/node
npm run dev
npm install zustand
npm install
```
## Running the Application

### Build and Run the Back-end Server

From the project's root directory (make sure docker already installed in your PC):

```bash
cd VisX.AI_Application/
docker-compose up --build
```

The Django server initiates the process by downloading the necessary Docker images and copying local folders into each image. It then installs the required packages as specified in each microservice’s requirement.txt files. After that, exposing PORT and run entrypoint.sh to perform database migrations and starts all microservices (refer to Dockerfile of each microservice for the detail), including:

- Gateway Service – Forwards frontend requests to the appropriate backend services.

- Modality Service – Manages data types (modalities), explanation methods, and related tasks.

- Upload Service – Handles uploading of models and datasets.

- Explanation Service – Processes and generates AI explanation results.

To view the database, the project is using PgAdmin, go to "http://localhost:8081/login?next=/browser/":

- Username: admin@admin.com

- Password: admin

Then "Add new server", for example viewing the upload database:

- Server name: upload_db

- Go to tab Connection

- Host name: upload_db

- Username: upload_user

- Password: upload_pass

- Save

- Now you can see the server connection (upload_db) on the left corner.

- Go to /upload_db/Databases/upload_db/Schemas/public/Tables/

- Here you can see all table of upload database.

Please refer to .env file of each microservice to see the database, port configurations.

To view the object storage MinIO, go to "http://localhost:9001/login":

- Username: minioadmin

- Password: minioadmin

### Run the Front-end Server

In a new terminal window, navigate to the `frontend/visxai_app/` directory:

```bash
cd frontend/visxai_app/
npm run dev
```
The Next.js server will start at `http://localhost:3000/`.

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostGRESQL Documentation](https://www.postgresql.org/docs/)
- [MinIO Documentation](https://min.io/docs/kes/)
- [Docker Documentation](https://docs.docker.com/)

## Contact

For any questions or issues, please reach out to the development team:

- **Project Maintainer**: EAA App Team

---

© 2025 EAA App Team. All rights reserved.