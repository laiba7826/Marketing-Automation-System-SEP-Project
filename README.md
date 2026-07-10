# Automation System - GFS Builders

A robust, role-based Marketing and Lead Management Automation System built with Flask and SQLite. This platform streamlines the workflow between Marketing, Content, Sales, and Management teams.

## 🚀 Technology Stack

- **Backend:** Python + Flask
- **Database:** SQLite3
- **Frontend:** Vanilla HTML5, CSS3, and JavaScript
- **Styling:** Custom CSS with support for multiple themes

## 🔄 System Flow & Architecture

The system operates on a hierarchical role-based access control (RBAC) model, ensuring each department has a tailored dashboard and specific permissions.

### Core Workflow:
1.  **Lead Generation:** Inquiries from the public site are captured and routed to the **Sales Team** or **Marketing Team**.
2.  **Budgeting & Planning:** The **Marketing Team** and **Content Creators** propose budget requests for campaigns or influencers.
3.  **Governance:** **Project Supervisors** review, approve, or counter-offer these budget requests.
4.  **Execution:** Approved campaigns are assigned to **Content Creators** who manage the content schedule and strategies.
5.  **Conversion:** The **Sales Team** tracks leads through various stages (New -> Contacted -> Closed) and records revenue.
6.  **Communication:** A global **Messaging System** allows roles to communicate and share updates directly within the portal.

## 👥 User Roles & Responsibilities

| Role | Key Responsibilities |
| :--- | :--- |
| **Admin** | Full system management: Users, Site Content, Global Settings, and System Logs. |
| **Project Supervisor** | High-level oversight, Budget Approval/Rejection, and Financial Reporting. |
| **Marketing Team** | Campaign planning, Budget requests, Lead tracking, and Content Creator assignment. |
| **Content Creator** | Strategy development, Influencer management, and Content scheduling. |
| **Sales Team** | Lead management, Revenue tracking, and Conversion optimization. |

## ✨ Key Features

- **Dynamic Sidebars:** Role-specific navigation menus tailored to user permissions.
- **Budget Management:** Full lifecycle of budget requests from proposal to approval/allocation.
- **Lead Pipeline:** Comprehensive lead management system for the Sales Team.
- **Content Scheduler:** Visual tracking of content deadlines and platforms.
- **Internal Messaging:** Secure role-based communication channel.
- **CMS (Content Management System):** Admin interface to update landing page content, features, and tech stack dynamically.

## 🛠️ Setup and Installation

1.  **Install Dependencies:**
    ```bash
    pip install flask
    ```
2.  **Initialize Database:**
    ```bash
    python init_db.py
    ```
3.  **Run Application:**
    ```bash
    python app.py
    ```
    The system will be available at `http://127.0.0.1:5000`.

---
*Created for GFS Builders Marketing Automation.*
