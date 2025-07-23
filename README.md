# XML Explorer

A powerful desktop application for XML file exploration and manipulation, featuring XPath queries and XSLT transformations with an intuitive graphical interface.

## 🚀 Features

### 📂 XML Data Exploration
- **File Loading**: Load and parse XML files with comprehensive error handling
- **Tree Visualization**: Interactive XML tree view with expandable/collapsible nodes
- **Syntax Highlighting**: Color-coded XML syntax for better readability
- **Document Structure Analysis**: Navigate through complex XML hierarchies

### 🔍 XPath Query Engine
- **Interactive XPath Execution**: Execute XPath queries with real-time results
- **Query History**: Automatic saving of executed queries for later reference
- **Favorites Management**: Save and organize frequently used XPath expressions
- **Result Highlighting**: Visual highlighting of matching nodes in the XML tree
- **Multiple Result Formats**: View results in different formats (text, nodes, attributes)

### 🔄 XSLT Transformations
- **XSLT Processing**: Apply XSLT stylesheets to transform XML documents
- **Live Preview**: Real-time HTML preview of transformation results
- **Template Management**: Load and manage multiple XSLT templates
- **Export Options**: 
  - Export to HTML files
  - Generate PDF documents
  - Save transformed XML

### 💻 User Interface
- **Modern Desktop GUI**: Clean, responsive interface built with Python Tkinter
- **Multi-panel Layout**: Organized workspace with tabbed panels
- **Theme Support**: Modern color scheme with syntax highlighting
- **Keyboard Shortcuts**: Efficient workflow with keyboard navigation

## 📋 Prerequisites

- Python 3.7 or higher
- Required Python libraries:
  - `tkinter` (usually included with Python)
  - `lxml`
  - `playwright`
- Operating System: Windows, macOS, or Linux

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/HananeAmilk/XML_Projects.git
cd XPath_XSTL_Explorer

# Install dependencies
pip install -r requirements.txt

# Or install dependencies manually
pip install lxml playwright

# Install Playwright browsers (for PDF export)
playwright install

# Run the application
python XMLExplorer.py
```

## 🎯 Quick Start

1. **Launch the Application**
   ```bash
   python XMLExplorer.py
   ```

2. **Load an XML File**
   - Click `Fichier > Ouvrir XML` or use `Ctrl+O`
   - Select your XML file from the file dialog
   - The XML tree will appear in the right panel with syntax highlighting

3. **Execute XPath Queries**
   - Navigate to the XPath query panel
   - Enter your XPath expression (e.g., `//book[@genre='fiction']`)
   - Click `Exécuter` or press `Enter`
   - View results in the results panel

4. **Apply XSLT Transformations**
   - Load an XSLT stylesheet using `Fichier > Ouvrir XSLT`
   - Click `Transformer` in the XSLT tab
   - Preview the HTML output in the preview tab
   - Export results using `Fichier > Export`

## 📚 Usage Examples

### XPath Queries
Sample XML and XSLT files are provided in the repository for testing and learning purposes. You can find these example files in the project directory to experiment with different XPath expressions and XSLT transformations.

## 🎥 Demo

### Video Demonstration

Watch our comprehensive demonstration video to see XML Explorer in action:

**📹  [Watch demo on YouTube](https://youtu.be/Hsc4JuCFbhI)

> **Note**: Click the link above to download and view the demonstration video, or view it directly in GitHub by clicking on the video file in the repository.

## ⚡ Key Features in Detail

### XML Tree Visualization
- Hierarchical tree representation of XML structure
- Expandable/collapsible nodes for easy navigation
- Attribute display in tree nodes
- Search functionality within the tree
- Syntax highlighting with color-coded elements

### XPath Query Management
- **History**: Automatically saves all executed queries with navigation (Up/Down arrows)
- **Favorites**: Star important queries for quick access (★ Favori button)
- **Validation**: Real-time XPath syntax validation
- **Results Export**: Export query results to various formats
- **Threaded Execution**: Non-blocking query execution for large XML files

### XSLT Processing Engine
- Support for XSLT 1.0 and 2.0
- Parameter passing to XSLT stylesheets
- Error handling with detailed error messages
- Template caching for improved performance
- Live HTML preview with syntax highlighting

### Advanced Features
- **PDF Export**: Generate PDF documents using Playwright
- **Multi-threaded Loading**: Non-blocking file operations
- **Settings Persistence**: Automatic saving of history, favorites, and preferences
- **Comprehensive Error Handling**: User-friendly error messages and logging
- **Built-in Help**: XPath and XSLT reference guides

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


**Made with ❤️ for XML developers and data analysts**
