from flask import Flask, request, jsonify

app = Flask(__name__)

def is_palindrome(s):
    """Check if a string is a palindrome, ignoring non-alphanumeric characters and case."""
    cleaned = ''.join(e for e in s if e.isalnum()).lower()
    return cleaned == cleaned[::-1], cleaned

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Palindrome Checker</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: #fafafa;
            padding: 2rem;
            color: #1a1a1a;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        h1 {
            font-size: 24px;
            font-weight: 500;
            margin-bottom: 2rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
            font-weight: 500;
        }

        input[type="text"] {
            width: 100%;
            padding: 10px 12px;
            font-size: 16px;
            border: 0.5px solid #ddd;
            border-radius: 8px;
            font-family: inherit;
            transition: border-color 0.2s;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #999;
            background: #f9f9f9;
        }

        .result {
            padding: 1rem;
            background: #f5f5f5;
            border-radius: 8px;
            border: 0.5px solid #ddd;
            margin-bottom: 1.5rem;
            display: none;
        }

        .result.show {
            display: block;
        }

        .result-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }

        .result-icon {
            font-size: 20px;
            font-weight: bold;
        }

        .result-icon.success {
            color: #16a34a;
        }

        .result-icon.error {
            color: #dc2626;
        }

        .result-text {
            font-size: 15px;
            font-weight: 500;
        }

        .result-text.success {
            color: #16a34a;
        }

        .result-text.error {
            color: #dc2626;
        }

        .result-divider {
            border-top: 0.5px solid #ddd;
            padding-top: 12px;
        }

        .cleaned-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 6px;
        }

        .cleaned-text {
            font-size: 14px;
            font-family: 'Monaco', 'Courier New', monospace;
            color: #1a1a1a;
            word-break: break-all;
            background: white;
            padding: 8px;
            border-radius: 4px;
            border: 0.5px solid #ddd;
        }

        .button-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
        }

        button {
            padding: 8px 12px;
            font-size: 14px;
            background: white;
            border: 0.5px solid #ddd;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            font-family: inherit;
        }

        button:hover {
            background: #f9f9f9;
            border-color: #999;
        }

        button:active {
            transform: scale(0.98);
        }

        .error-message {
            color: #dc2626;
            font-size: 14px;
            margin-top: 8px;
            display: none;
        }

        .error-message.show {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Palindrome checker</h1>

        <div class="form-group">
            <label for="inputText">Enter text</label>
            <input
                type="text"
                id="inputText"
                placeholder="e.g., A man, a plan, a canal: Panama"
            />
            <div class="error-message" id="errorMessage"></div>
        </div>

        <div id="resultContainer" class="result">
            <div class="result-header">
                <span id="resultIcon" class="result-icon"></span>
                <span id="resultText" class="result-text"></span>
            </div>
            <div class="result-divider">
                <p class="cleaned-label">Cleaned text</p>
                <p id="cleanedText" class="cleaned-text"></p>
            </div>
        </div>

        <div class="button-group">
            <button onclick="testExample('racecar')">racecar</button>
            <button onclick="testExample('hello')">hello</button>
            <button onclick="testExample('A Santa at NASA')">A Santa at NASA</button>
        </div>
    </div>

    <script>
        async function checkPalindrome() {
            const input = document.getElementById('inputText').value;
            const resultContainer = document.getElementById('resultContainer');
            const errorMessage = document.getElementById('errorMessage');

            if (!input.trim()) {
                resultContainer.classList.remove('show');
                errorMessage.classList.remove('show');
                return;
            }

            try {
                const response = await fetch('/api/check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: input })
                });

                const data = await response.json();

                if (data.error) {
                    errorMessage.textContent = data.error;
                    errorMessage.classList.add('show');
                    resultContainer.classList.remove('show');
                    return;
                }

                errorMessage.classList.remove('show');

                const icon = document.getElementById('resultIcon');
                const text = document.getElementById('resultText');

                if (data.isPalindrome) {
                    icon.textContent = '✓';
                    icon.className = 'result-icon success';
                    text.textContent = 'Is a palindrome';
                    text.className = 'result-text success';
                } else {
                    icon.textContent = '✗';
                    icon.className = 'result-icon error';
                    text.textContent = 'Not a palindrome';
                    text.className = 'result-text error';
                }

                document.getElementById('cleanedText').textContent = data.cleaned || '(empty)';
                resultContainer.classList.add('show');
            } catch (error) {
                errorMessage.textContent = 'Error checking palindrome';
                errorMessage.classList.add('show');
                resultContainer.classList.remove('show');
            }
        }

        function testExample(text) {
            document.getElementById('inputText').value = text;
            checkPalindrome();
        }

        document.getElementById('inputText').addEventListener('input', checkPalindrome);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML

@app.route('/api/check', methods=['POST'])
def check():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text.strip():
        return jsonify({'error': 'Please enter some text'})
    
    is_pal, cleaned = is_palindrome(text)
    
    return jsonify({
        'isPalindrome': is_pal,
        'cleaned': cleaned,
        'original': text
    })

if __name__ == '__main__':
    app.run(debug=True)
