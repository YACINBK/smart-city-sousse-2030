# Smart City Sousse 2030

An academic database project for smart city development in Sousse, Tunisia, focusing on data management, real-time simulation, and dashboard visualization for urban planning and monitoring.

## 📋 About

Smart City Sousse 2030 is an academic project that implements a comprehensive database system for managing and monitoring smart city infrastructure and services. The project includes data generation, real-time simulation, dashboard visualization, and database management capabilities to support the vision of transforming Sousse into a smart city by 2030.

## 🎯 Project Goals

- **Database Management**: Design and implement a robust database schema for smart city data
- **Real-time Simulation**: Simulate real-time smart city sensor data and events
- **Data Visualization**: Provide dashboard interfaces for monitoring city metrics
- **Data Generation**: Generate realistic datasets for testing and development
- **Urban Planning**: Support data-driven decision making for urban development

## 📁 Project Structure

```
smart-city-sousse-2030/
├── smartcity_backend/              # Backend application module
├── dashboard.py                    # Dashboard visualization application
├── generate_data.py                # Data generation script
├── simulate_realtime.py            # Real-time data simulation
├── manage.py                       # Django management script (if applicable)
├── schema.sql                      # Database schema definition
├── requirements.txt                # Python dependencies
├── rapport_projet_smart_city.md    # Project report (Markdown)
├── rapport_projet_smart_city.tex   # Project report (LaTeX)
├── theorie_corrigee.md             # Theory documentation
├── bdd.pdf                         # Database documentation
├── bdd-theorie.pdf                 # Database theory
├── Projet Module 25-26.pdf         # Project module documentation
└── prompt.txt                      # Project prompts/requirements
```

## 🛠️ Technologies Used

- **Python** (89.6%): Main programming language for data processing and applications
- **TeX/LaTeX** (10.4%): Documentation and report generation
- **SQL**: Database schema and queries
- **Django/Flask** (likely): Backend web framework
- **Data Visualization**: Dashboard libraries (Plotly, Dash, or similar)

## 📦 Prerequisites

- **Python**: 3.7 or higher
- **Database**: PostgreSQL, MySQL, or SQLite
- **pip**: Python package manager

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/OussemaBenAmeur/smart-city-sousse-2030.git
cd smart-city-sousse-2030
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
# Using the provided schema
mysql -u username -p < schema.sql
# Or for PostgreSQL:
psql -U username -d database_name -f schema.sql
# Or for SQLite:
sqlite3 smartcity.db < schema.sql
```

5. Configure database connection:
   - Update database credentials in the application configuration files
   - Set environment variables if required

## 💻 Usage

### Data Generation

Generate sample data for testing:
```bash
python generate_data.py
```

### Real-time Simulation

Run real-time data simulation:
```bash
python simulate_realtime.py
```

### Dashboard

Launch the dashboard application:
```bash
python dashboard.py
```

The dashboard will typically be accessible at `http://localhost:5000` or the configured port.

### Backend Server

If using Django, run the development server:
```bash
python manage.py runserver
```

For Flask or other frameworks, follow the specific startup instructions in the backend module.

## 📊 Features

### Database Management
- **Schema Design**: Comprehensive database schema for smart city entities
- **Data Modeling**: Entities for sensors, infrastructure, citizens, services, etc.
- **Query Optimization**: Efficient database queries for large datasets

### Data Simulation
- **Real-time Data**: Simulate sensor data streams (traffic, air quality, energy, etc.)
- **Event Generation**: Generate smart city events and alerts
- **Historical Data**: Create historical datasets for analysis

### Dashboard Visualization
- **Real-time Monitoring**: Live dashboards for city metrics
- **Analytics**: Data analysis and visualization
- **Reporting**: Generate reports and insights

### Data Generation
- **Synthetic Data**: Generate realistic smart city datasets
- **Testing Support**: Create test data for development
- **Benchmarking**: Generate data for performance testing

## 🏗️ Smart City Components

The project likely covers various smart city domains:

- **Transportation**: Traffic monitoring, public transit, parking management
- **Environment**: Air quality, waste management, water systems
- **Energy**: Smart grids, consumption monitoring, renewable energy
- **Infrastructure**: Buildings, roads, public spaces
- **Services**: Healthcare, education, public safety
- **Citizen Services**: Digital services, citizen engagement

## 📚 Documentation

- **`rapport_projet_smart_city.md`**: Complete project report in Markdown format
- **`rapport_projet_smart_city.tex`**: LaTeX version of the project report
- **`theorie_corrigee.md`**: Theoretical foundations and corrections
- **`bdd.pdf`**: Database design documentation
- **`bdd-theorie.pdf`**: Database theory and concepts
- **`Projet Module 25-26.pdf`**: Module-specific documentation

## 🔍 Development

### Database Schema

Review and understand the database schema:
```bash
cat schema.sql
```

### Testing

Test the database connection and queries:
```bash
python -c "from smartcity_backend import db; db.test_connection()"
```

### Configuration

Configure the application settings:
- Database connection strings
- API keys (if needed)
- Port numbers
- Logging levels

## 📖 Academic Context

This is an academic database project, likely part of:
- Database Systems course
- Smart City or Urban Planning module
- Final year project or capstone

The project demonstrates:
- Database design and implementation
- Data modeling and normalization
- Query optimization
- Application development with databases
- Real-time data processing
- Data visualization

## 🤝 Contributing

This is an academic project. Contributions, suggestions, and improvements are welcome:

- Bug fixes
- Documentation improvements
- Feature enhancements
- Performance optimizations
- Code refactoring

Please feel free to submit a Pull Request!

## 📝 License

This project is open source and available for educational and academic purposes.

## 👥 Authors

This project was developed collaboratively by:

**Yacin Ben Kacem**
- GitHub: [@YACINBK](https://github.com/YACINBK)

**Oussema Ben Ameur**
- GitHub: [@OussemaBenAmeur](https://github.com/OussemaBenAmeur)

## 🌍 About Sousse

Sousse is a coastal city in Tunisia, and this project envisions its transformation into a smart city by 2030. The project aims to support sustainable urban development through technology and data-driven solutions.

## 📌 Note

This is an academic project created as part of a module/course. The project structure and implementation follow academic requirements and may include theoretical components and documentation beyond typical production applications.

## 🚀 Future Enhancements

Potential areas for future development:
- IoT sensor integration
- Machine learning for predictive analytics
- Mobile application development
- API development for third-party integrations
- Cloud deployment
- Advanced visualization and analytics
- Citizen engagement platforms

---

⭐ If you find this project useful, please consider giving it a star!

🏙️ Building the smart city of tomorrow, today!
