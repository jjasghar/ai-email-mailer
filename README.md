# AI Email Mailer

A Django web application that uses Ollama AI to send personalized emails. Each recipient receives a unique, AI-rewritten version of your seed email while maintaining the core message and information.

## ✨ Features

### Core Functionality
- **AI-Powered Email Rewriting**: Uses Ollama to generate unique email content for each recipient
- **Seed Email Management**: Create and manage base email templates in Markdown format
- **HTML Templates**: Add professional headers and footers to your emails
- **Campaign Management**: Create, copy, and manage email campaigns
- **Real-Time Progress Tracking**: Monitor email sending progress with live updates

### Recipient Management
- **CSV Import**: Bulk import recipients with email, name, company, and phone
- **Manual Entry**: Add recipients individually or via text input
- **Search & Filter**: Quickly find recipients by name, company, email, or domain
- **Select All**: Easily select all or filtered recipients for campaigns
- **Edit Recipients**: Update recipient information including name, company, and phone

### Advanced Features
- **Variable Detection**: Automatically detects variables in seed emails (e.g., `[insert dates]`, `%recipient name%`, `(insert value)`)
- **Variable Mapping**: Map variables to recipient fields (name, company, phone, email) or custom values
- **Campaign Copying**: Duplicate campaigns with different recipient lists
- **Email History**: Track all sent emails with full content records

## 🚀 Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running
- An Ollama model (e.g., `granite4:1b`, `llama2`, `mistral`)
- SMTP email account (Gmail, Outlook, SendGrid, Mailgun, etc.)

## 📦 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/ai-newsletter-mailer.git
cd ai-newsletter-mailer
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

5. **Run migrations:**
```bash
python manage.py migrate
```

6. **Create superuser (optional, for admin access):**
```bash
python manage.py createsuperuser
```

7. **Start the development server:**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## ⚙️ Configuration

### Environment Variables

The `.env.example` file includes all required configuration. Key settings:

#### Django Settings
- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed domains

#### Database
- `DATABASE_URL`: Database connection string (defaults to SQLite)
  - SQLite: `sqlite:///db.sqlite3`
  - PostgreSQL: `postgres://user:password@localhost:5432/email_mailer`
  - MySQL: `mysql://user:password@localhost:3306/email_mailer`

#### Email Settings
Configure your SMTP server settings:
- `EMAIL_HOST`: SMTP server (e.g., `smtp.gmail.com`)
- `EMAIL_PORT`: SMTP port (usually `587` for TLS)
- `EMAIL_USE_TLS`: Set to `True` for TLS encryption
- `EMAIL_HOST_USER`: Your email address
- `EMAIL_HOST_PASSWORD`: Your email password or app password
- `DEFAULT_FROM_EMAIL`: Sender email address

**Note for Gmail users:** You'll need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

#### Ollama Settings
- `OLLAMA_API_URL`: Ollama API endpoint (default: `http://localhost:11434/api/generate`)
- `OLLAMA_MODEL`: Model to use for rewriting (e.g., `granite4:1b`, `llama2`)

### Setting Up Ollama

1. **Install Ollama:**
   - Visit [ollama.ai](https://ollama.ai/) and follow installation instructions
   - Or use: `curl -fsSL https://ollama.ai/install.sh | sh`

2. **Start Ollama:**
```bash
ollama serve
```

3. **Pull a model:**
```bash
ollama pull granite4:1b
# or
ollama pull llama2
```

4. **List available models:**
```bash
ollama list
```

## 📖 Usage

### 1. Create a Seed Email

Write your base email content in Markdown format. You can include variables that will be replaced:

- `[insert dates]` - Square brackets
- `%recipient name%` - Percent signs
- `(insert value)` - Parentheses
- `{variable name}` - Curly braces

**Example:**
```markdown
Hello %recipient name%,

We're excited to announce our event on [event date].

Best regards,
Your Team
```

### 2. Create an Email Template (Optional)

Add HTML header and footer to wrap your email content. This is useful for branding and consistent styling.

### 3. Add Recipients

#### CSV Import
Create a CSV file with the following columns (in order):
1. Email (required)
2. Name (optional)
3. Company (optional)
4. Phone (optional)

**Example CSV:**
```csv
email@example.com,John Doe,Acme Corp,555-1234
jane@example.com,Jane Smith,Tech Inc,555-5678
bob@example.com,Bob Johnson
```

#### Manual Entry
- Add recipients one at a time via the web interface
- Or paste multiple email addresses (one per line)

### 4. Create a Campaign

1. Select a seed email
2. Choose recipients (use search to filter, select all for bulk selection)
3. Optionally select an email template
4. Configure variable mappings if variables were detected in your seed email
5. Add optional AI prompt for additional rewriting instructions

### 5. Send Campaign

1. Review your campaign details
2. Click "Send Campaign"
3. Monitor real-time progress as emails are sent
4. Each recipient receives a unique, AI-rewritten version

### 6. Copy Campaigns

Want to reuse a campaign with different recipients? Use the "Copy Campaign" feature to duplicate all settings and select a new recipient list.

## 🔧 Advanced Features

### Variable Mapping

When creating a campaign, if your seed email contains variables, you'll see a variable mapping form. For each variable, you can:

- **Map to recipient fields**: Automatically use recipient's name, company, phone, or email
- **Use custom values**: Enter a fixed value that applies to all recipients

Variables are replaced before AI rewriting, so the AI can naturally incorporate them into the personalized content.

### Real-Time Progress

When sending a campaign, you'll see:
- Progress bar with percentage
- Current email being processed
- Count of emails sent vs. total
- Status updates

The page automatically redirects to the campaign detail page when complete.

## 📁 Project Structure

```
ai-newsletter-mailer/
├── emails/                 # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── services.py         # Email sending logic
│   ├── utils.py            # Utility functions (AI integration, variable detection)
│   └── urls.py             # URL routing
├── newsletter_mailer/     # Django project settings
│   ├── settings.py         # Application settings
│   └── urls.py             # Root URL configuration
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   └── emails/            # Email-related templates
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🛠️ Technology Stack

- **Backend**: Django 5.0+
- **AI**: Ollama (local LLM)
- **Database**: SQLite (default), PostgreSQL, MySQL supported
- **Frontend**: Bootstrap 5
- **Email**: Django SMTP backend

## 📝 CSV Format Reference

The CSV file format supports the following columns (in order):

| Column | Required | Description |
|--------|----------|-------------|
| Email  | Yes      | Recipient's email address |
| Name   | No       | Recipient's name |
| Company| No       | Company name |
| Phone  | No       | Phone number |

**Examples:**

Minimal (email only):
```csv
email@example.com
another@example.com
```

With name:
```csv
email@example.com,John Doe
another@example.com,Jane Smith
```

Full format:
```csv
email@example.com,John Doe,Acme Corp,555-1234
another@example.com,Jane Smith,Tech Inc,555-5678
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for providing local LLM capabilities
- [Django](https://www.djangoproject.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for the UI framework

## 🐛 Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check that `OLLAMA_API_URL` in `.env` matches your Ollama instance
- Verify the model is installed: `ollama list`

### Email Sending Issues
- Verify SMTP settings in `.env`
- For Gmail, use an App Password, not your regular password
- Check that `EMAIL_HOST`, `EMAIL_PORT`, and `EMAIL_USE_TLS` are correct
- Test SMTP connection outside the application first

### Variable Not Replacing
- Ensure variable names match exactly (case-insensitive)
- Check that variable mappings are configured in the campaign
- Variables are replaced before AI rewriting

---

**Note**: This application sends emails using your configured SMTP server. Ensure you comply with email regulations (CAN-SPAM, GDPR, etc.) and have proper consent from recipients.
