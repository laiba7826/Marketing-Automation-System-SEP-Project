import sqlite3

def init_db():
    connection = sqlite3.connect('database.db')
    
    with open('schema.sql') as f:
        connection.executescript(f.read())
    
    cursor = connection.cursor()

    # Seed Site Content
    content = [
        ('global', 'site', 'title', 'GFS Marketing Automation'),
        ('global', 'footer', 'description', 'Streamline your campaigns with our end-to-end management system.'),
        ('global', 'footer', 'copyright', '&copy; 2024 GFS Marketing Automation. All Rights Reserved.'),
        ('home', 'hero', 'title', 'GFS Marketing Automation System'),
        ('home', 'hero', 'subtitle', 'Streamline Your Campaigns with End-to-End Management for Marketing, Content, Sales, and Project Teams.'),
        ('home', 'why_gfs', 'title', 'Why Choose GFS?'),
        ('home', 'why_gfs', 'desc', 'Say goodbye to scattered spreadsheets and endless email threads. GFS brings your entire marketing workflow into one central hub.'),
        ('home', 'cta', 'title', 'Ready to Optimize Your Marketing?'),
        ('home', 'cta', 'subtitle', 'Join thousands of teams using GFS to drive results.')
    ]
    cursor.executemany('INSERT INTO site_content (page, section, key, value) VALUES (?, ?, ?, ?)', content)

    # Seed Budget Requests
    cursor.execute('INSERT INTO budget_requests (title, type, amount, proposed_by, status, progress, assigned_to) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 ('Summer Sale 2025', 'Campaign', 8000.0, 'Marketing Team', 'Approved', 25, 4))
    cursor.execute('INSERT INTO budget_requests (title, type, amount, proposed_by, status, progress, assigned_to) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 ('Influencer Outreach Q3', 'Influencer', 4500.0, 'Content Creator', 'Pending', 0, None))

    # Seed Features
    features = [
        ('Campaign Workflow', 'Automated approval chains ensure no step is missed, from proposal to launch, keeping everyone aligned.', 'fas fa-tasks'),
        ('Budget Management', 'Precise controls for allocating, tracking, and approving budgets for various campaigns and influencer payments.', 'fas fa-coins'),
        ('Content Scheduling', 'Visual calendar for planning posts across platforms. collaborate with your team to ensure consistent messaging.', 'fas fa-calendar-alt'),
        ('Influencer Collaboration', 'Manage relationships, contracts, and deliverables with external partners directly within the portal.', 'fas fa-users'),
        ('Sales Reporting', 'Connect marketing efforts to sales data. Visualize ROI and track progress with dynamic dashboards.', 'fas fa-chart-line'),
        ('Role-Based Access', 'Secure Admin Dashboard to manage users, roles, and system settings, ensuring data security and integrity.', 'fas fa-user-shield')
    ]
    cursor.executemany('INSERT INTO site_features (title, description, icon) VALUES (?, ?, ?)', features)

    # Create users with profile info
    users = [
        ('admin', 'admin123', 'Admin', 'Admin User', 'admin@gfsbuilders.com', '+92 311 0001111'),
        ('marketing', 'market123', 'Marketing Team', 'Sarah Khan', 'marketing@gfsbuilders.com', '+92 311 2223333'),
        ('supervisor', 'super123', 'Project Supervisor', 'Supervisor User', 'supervisor@gfsbuilders.com', '+92 311 4445555'),
        ('creator', 'creator123', 'Content Creator', 'Content Team', 'creator@gfsbuilders.com', '+92 311 6667777'),
        ('sales', 'sales123', 'Sales Team', 'Sales Team', 'sales@gfsbuilders.com', '+92 311 8889999')
    ]
    cursor.executemany('INSERT INTO users (username, password, role, full_name, email, phone) VALUES (?, ?, ?, ?, ?, ?)', users)

    # Seed Tech Stack
    tech = [
        ('Frontend', 'HTML5, CSS3, JavaScript', 'A responsive, semantic, and interactive user interface designed with modern web standards.', 'fab fa-html5'),
        ('Backend', 'Python & Flask', 'A lightweight yet powerful micro-framework that handles routing, logic, and secure data processing.', 'fab fa-python'),
        ('Database', 'SQLite', 'A reliable, serverless SQL database engine ensuring fast data retrieval and persistent storage.', 'fas fa-database')
    ]
    cursor.executemany('INSERT INTO site_tech_stack (category, title, description, icon) VALUES (?, ?, ?, ?)', tech)

    # Seed Steps (How It Works)
    steps = [
        ('Campaign Proposal', 'The Marketing Team proposes a comprehensive campaign plan, outlining goals, target audience, and strategies.', 'fas fa-lightbulb'),
        ('Initial Approval', 'The Project Supervisor reviews the campaign goals. Upon approval, the Marketing Team is notified.', 'fas fa-search-dollar'),
        ('Budget Authorization', 'The Supervisor approves the budget. Once authorized, the plan is shared with Content Creators.', 'fas fa-file-invoice-dollar'),
        ('Content & Collaboration', 'Content Creators schedule posts and manage influencer collaborations.', 'fas fa-video'),
        ('Payment & Reporting', 'Creators request payments, Supervisor approves, and Sales Team tracks revenue.', 'fas fa-credit-card')
    ]
    cursor.executemany('INSERT INTO site_steps (title, description, icon) VALUES (?, ?, ?)', steps)

    # Seed Messages
    messages = [
        (3, 'supervisor', 'Project Supervisor', 'Marketing Team', 'Welcome', 'Welcome to the system! Let me know if you need help.'),
        (2, 'marketing', 'Marketing Team', 'Project Supervisor', 'Summer Sale Budget', 'I have submitted the budget for the Summer Sale.'),
    ]
    cursor.executemany('INSERT INTO messages (sender_id, sender_name, sender_role, receiver_role, subject, content) VALUES (?, ?, ?, ?, ?, ?)', messages)

    # Seed Strategies
    strategies = [
        (1, 4, 'Social Media Blast', 'We will use Instagram and Facebook ads to target people aged 18-35.'),
        (1, 4, 'Influencer Video', 'A 60-second video on YouTube showing the benefits of our system.')
    ]
    cursor.executemany('INSERT INTO campaign_strategies (campaign_id, creator_id, title, content) VALUES (?, ?, ?, ?)', strategies)

    # Seed Roles & Access Details
    roles = [
        ('Admin', 'fas fa-shield-alt', 'Full system control and management of users and site content.', 
         'Manage user accounts;Configure system-wide settings;Update landing page content;Full dashboard overview'),
        ('Project Supervisor', 'fas fa-user-tie', 'Oversees projects, approves budgets, and manages training.', 
         'Approve budget requests;Send counter-offers for campaigns;Track allocated budget;Schedule training sessions'),
        ('Marketing Team', 'fas fa-bullhorn', 'Proposes campaigns and manages marketing strategies.', 
         'Propose campaign budget;Track campaign goals;Assign content creators;View marketing inquiries'),
        ('Content Creator', 'fas fa-pen-nib', 'Creates content and manages influencer collaborations.', 
         'Draft campaign strategies;Request influencer budget;Manage content schedule;Track assigned tasks'),
        ('Sales Team', 'fas fa-chart-line', 'Manages leads and tracks sales performance.', 
         'Manage sales leads;Record revenue;View sales reports;Track ROI analytics')
    ]
    cursor.executemany('INSERT INTO site_roles (role_name, icon, description, permissions) VALUES (?, ?, ?, ?)', roles)

    connection.commit()
    connection.close()
    print("Database initialized and seeded successfully.")

if __name__ == '__main__':
    init_db()
