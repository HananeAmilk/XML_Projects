# XML to MySQL Database Importer

A Python GUI application that allows you to import XML data directly into a MySQL database with an intuitive interface.

## Features

- **Easy-to-use GUI**: Built with tkinter for a user-friendly experience
- **MySQL Connection Management**: Connect to local or remote MySQL servers
- **Database Creation**: Create new databases directly from the application
- **Automatic Table Generation**: Automatically creates tables based on XML structure
- **Data Import**: Imports XML data into MySQL tables with proper data mapping
- **Real-time Logging**: Monitor the import process with timestamped logs
- **Error Handling**: Comprehensive error handling for XML parsing and database operations

## Prerequisites

- Python 3.7 or higher
- MySQL Server (local or remote)
- Required Python packages (see Installation section)

## Installation

1. **Clone or download the project files**
   ```bash
   git clone https://github.com/HananeAmilk/XML_Projects.git
   cd XML_to_MySQL_Project
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install customtkinter==5.2.2
   pip install darkdetect==0.8.0
   pip install mysql-connector-python==9.3.0
   pip install packaging==25.0
   pip install pillow==11.2.1
   ```

3. **Ensure MySQL Server is running**
   - Install MySQL Server if not already installed
   - Make sure the MySQL service is running
   - Have your MySQL credentials ready

## Usage

### Starting the Application

Run the application using Python:
```bash
python xml_to_db_app_v2.py
```

### Step-by-Step Guide

#### 1. Configure MySQL Connection
Fill in the MySQL connection details:
- **Host**: MySQL server address (default: localhost)
- **Port**: MySQL server port (default: 3306)
- **Username**: Your MySQL username
- **Password**: Your MySQL password
- **Database**: Target database name

#### 2. Connect to Database
- Click **"Connecter"** to establish connection to an existing database
- Or click **"Créer Base de Données"** to create a new database

#### 3. Select XML File
- Click **"Parcourir"** to select your XML file
- Supported format: `.xml` files

#### 4. Import Data
- Click **"Importer XML vers la base de données"**
- Monitor the progress in the log panel
- Check the status bar for connection information

### XML Structure Requirements

The application expects XML files with the following structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<root_element>
    <item>
        <column1>value1</column1>
        <column2>value2</column2>
        <column3>value3</column3>
    </item>
    <item>
        <column1>value4</column1>
        <column2>value5</column2>
        <column3>value6</column3>
    </item>
</root_element>
```

**Key Points:**
- The root element name becomes the table name
- First child element structure defines the table columns
- Each child element becomes a database record
- Column names are derived from XML tag names

## How It Works

### Database Table Creation
1. Analyzes the first child element in the XML to determine column structure
2. Creates a MySQL table named after the XML root element
3. Adds an auto-increment `id` column as primary key
4. All data columns are created as `TEXT` type for flexibility

### Data Import Process
1. Parses the entire XML file
2. Extracts data from each child element
3. Maps XML elements to database columns
4. Inserts data row by row into the MySQL table
5. Handles missing elements by inserting NULL values

### Error Handling
- **XML Parsing Errors**: Invalid XML format detection
- **MySQL Connection Errors**: Connection failure notifications  
- **Database Errors**: SQL execution error handling
- **File Access Errors**: Missing or inaccessible file handling

## Example

### Sample XML File (`products.xml`)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<products>
    <product>
        <name>Laptop</name>
        <price>999.99</price>
        <category>Electronics</category>
        <stock>50</stock>
    </product>
    <product>
        <name>Mouse</name>
        <price>25.99</price>
        <category>Electronics</category>
        <stock>200</stock>
    </product>
</products>
```

### Resulting MySQL Table
**Table Name**: `products`

| id | name   | price  | category    | stock |
|----|--------|--------|-------------|-------|
| 1  | Laptop | 999.99 | Electronics | 50    |
| 2  | Mouse  | 25.99  | Electronics | 200   |

## Troubleshooting

### Common Issues

**"Connection Error"**
- Verify MySQL server is running
- Check host, port, username, and password
- Ensure the specified database exists (or create it using the app)

**"XML Parsing Error"**
- Verify XML file is well-formed and valid
- Check file encoding (UTF-8 recommended)
- Ensure XML follows the expected structure

**"No columns found"**
- XML must have at least one child element under the root
- Child elements must contain sub-elements (not just text)

**"Permission Denied"**
- Ensure MySQL user has CREATE, INSERT, and DROP privileges
- Check if database/table already exists and user can modify it

### Log Analysis
The application provides detailed logs with timestamps:
- Connection status messages
- XML parsing progress
- Table creation confirmations  
- Import progress and results
- Error details for troubleshooting

## Technical Details

### Dependencies
- **customtkinter**: Modern GUI framework for enhanced appearance
- **mysql-connector-python**: Official MySQL driver for Python
- **packaging**: Package version handling utilities
- **pillow**: Image processing library for GUI enhancements

### Database Schema
- All imported tables include an auto-increment `id` primary key
- Data columns use `TEXT` type for maximum compatibility
- Existing tables are dropped and recreated on each import
- NULL values are inserted for missing XML elements

### Performance Considerations
- Large XML files are processed sequentially
- Database commits are performed after all insertions
- Memory usage scales with XML file size
- No built-in progress bar for very large files

## License

This project is provided as-is for educational and personal use.


**Note**: This application is designed for development and testing purposes. For production use, consider implementing additional features like data validation, backup mechanisms, and enhanced security measures.
