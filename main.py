import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt  # Add this import
import re

from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtGui import QTextCursor
import ollama
import markdown

# Global constants
LLAMA_MODEL = "llama3.1:8b"  # Large model

# Doctor's name as a global variable
DR_NAME = "Dr. Hearwell"#"Dr Harmony Hearwell"#"Dr. Thomas Audley"

# Model configuration
MODEL_CONFIG = {
    "model": LLAMA_MODEL,
    # "options": {
    #     "temperature": 0.7, # Higher temperature: more randomness
    #     "top_p": 0.9, # Higher top_p: more diversity
    #     "top_k": 40, # 0 means no top_k filtering
    #     "num_ctx": 4096, # Max context window size
    #     "repeat_penalty": 1.1, # Higher penalty: more diverse responses
    #     "stop": ["User:", "Human:", "Assistant:"]# Stop generation at these tokens
    # }
}
class ChatbotApp(QMainWindow):
    """
    A PyQt-based chatbot application specialized for hearing loss related queries.
    This application provides a graphical user interface for interacting with an Ollama-powered
    chatbot that answers questions about hearing loss. It features a chat history display,
    pre-made questions, and the ability to ask custom questions.
    Attributes:
        chat_history (QTextEdit): Display area for conversation history.
        user_input (QLineEdit): Input field for user messages.
        personal_question_input (QLineEdit): Input field for personal questions.
    Methods:
        send_message(): Processes and sends the user's message from the main input field.
        send_premade_question(question: str): Handles pre-made question button interactions.
        send_personal_question(): Processes and sends the user's personal question.
    """
    def __init__(self):
        super().__init__()
        
        # Initialize message history with system message
        self.message_history = [{
            "role": "system",
            "content": f"""You are a hearing doctor ({DR_NAME}) participating in an outreach activity explaining hearing loss
              and auditory neuroscience to the public.
            Be positive and relatively short in the responses, but not too concise. If you are unsure do not invent answers, 
            just say that you do not know.
            Target a young audience, 15-30 years old. Do not mention the following unless asked: if I ask you what you are, 
            answer that you are a computer software trained to talk about hearing and hearing loss
            made by the Hearing Research Group at the University of Sheffield, and mention briefly how a language model works 
            in simple terms.
            If asked to give medical advice, say that you are not a real doctor and that the person should consult a healthcare professional.
            You are also an expert in the neuroscience of hearing, especially the mammalian cochlea, hair cells, and the auditory nerve.
             """}]

        # Set up the main window with a gradient background
        self.setWindowTitle("Hearing Loss Chatbot")
        self.setGeometry(100, 100, 800, 600)  # Larger window size
        
        # Create central widget and layout
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #E0F7FA, stop:1 #B2EBF2);
                color: #006064;
                font-family: Arial;
            }
            QTextEdit {
                background-color: white;
                border: 2px solid #00BCD4;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #00BCD4;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
                margin: 5px;
            }
            QPushButton {
                background-color: #00BCD4;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #00ACC1;
            }
            QPushButton:pressed {
                background-color: #0097A7;
                padding: 12px 18px;
            }
        """)
        self.setCentralWidget(central_widget)
        
        # Create main layout with margins
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Create header layout
        header_layout = QHBoxLayout()
        main_layout.addLayout(header_layout)

        # Create vertical layout for logo and text
        logo_layout = QVBoxLayout()
        header_layout.addLayout(logo_layout)

        # Add title label
        title_label = QLabel("HearGPT: Your Hearing Loss Chatbot")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #006064;
            margin-left: 20px;
        """)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(title_label)

        # Add stretch to push everything to the left
        header_layout.addStretch()

        # Create a horizontal layout for the image and chat history
        image_chat_layout = QHBoxLayout()
        main_layout.addLayout(image_chat_layout)

        # Add an image of a doctor
        doctor_image = QLabel()
        pixmap = QPixmap("doctor.png")
        # Resize image to reasonable dimensions (e.g. 150x150)
        scaled_pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        doctor_image.setPixmap(scaled_pixmap)
        doctor_image.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        doctor_image.setStyleSheet("""
            QLabel {
                padding: 10px;
                margin: 5px;
                # background: white;
                border: 2px solid #00BCD4;
                border-radius: 10px;
            }
        """)
        image_chat_layout.addWidget(doctor_image)  # Uncomment this line

        # Update chat history styling
        self.chat_history = QTextEdit()
        self.chat_history.setAcceptRichText(True)
        self.chat_history.setReadOnly(True)

        # Set document margins to prevent scrollbar overlap
        self.chat_history.document().setDocumentMargin(20)

        self.chat_history.setStyleSheet("""
            QTextEdit {
                color: black;
                padding: 15px 25px 15px 15px;  /* top right bottom left */
                margin: 5px;
                border: 2px solid #00BCD4;
                border-radius: 10px;
                text-align: justify;
            }
            QTextEdit QWidget {
                text-align: justify;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #E0F7FA;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #00BCD4;
                border-radius: 6px;
                min-height: 20px;
            }
        """)
        image_chat_layout.addWidget(self.chat_history)

        # Create input layout
        input_layout = QHBoxLayout()
        main_layout.addLayout(input_layout)

        # Create a line edit for user input
        self.user_input = QLineEdit()
        self.user_input.setStyleSheet("color: black;")
        self.user_input.setPlaceholderText("Type your question here...")
        input_layout.addWidget(self.user_input)

        # Add after creating self.user_input
        self.user_input.returnPressed.connect(self.send_message)

        # Create a send button
        send_button = QPushButton("Send")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #00CED1;
                color: black;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                transition: background-color 0.2s;
            }
            QPushButton:hover {
                background-color: #00BCD4;
            }
            QPushButton:pressed {
                background-color: #0097A7;
                padding: 12px 18px;
            }
        """)
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)

        # Create a horizontal layout for pre-made question buttons
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        # Add pre-made question buttons
        questions = [
            "How does hearing work?",
            "How can I protect my hearing?",
            "What are the common causes of hearing loss?",
            "How does our hearing work?",  # New question
            "Can hearing loss be cured?",  # New question
            "What is tinnitus?"  # New question
        ]

        # Create two rows of buttons
        row1_questions = questions[:3]
        row2_questions = questions[3:]

        # First row of buttons (existing)
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        for question in row1_questions:
            button = QPushButton(question)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #00CED1;
                    color: black;
                    border: none;
                    border-radius: 10px;
                    padding: 10px 20px;
                    transition: background-color 0.2s;
                }
                QPushButton:hover {
                    background-color: #00BCD4;
                }
                QPushButton:pressed {
                    background-color: #0097A7;
                    padding: 12px 18px;
                }
            """)
            button.clicked.connect(lambda checked, q=question: self.send_premade_question(q))
            button_layout.addWidget(button)

        # Second row of buttons (new)
        button_layout2 = QHBoxLayout()
        main_layout.addLayout(button_layout2)

        for question in row2_questions:
            button = QPushButton(question)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #00CED1;
                    color: black;
                    border: none;
                    border-radius: 10px;
                    padding: 10px 20px;
                    transition: background-color 0.2s;
                }
                QPushButton:hover {
                    background-color: #00BCD4;
                }
                QPushButton:pressed {
                    background-color: #0097A7;
                    padding: 12px 18px;
                }
            """)
            button.clicked.connect(lambda checked, q=question: self.send_premade_question(q))
            button_layout2.addWidget(button)
        
        # Create contact info layout
        contact_layout = QHBoxLayout()
        main_layout.addLayout(contact_layout)

        # Add spacer to push contact info to bottom
        contact_layout.addStretch()

        # # Create Twitter link with icon
        # twitter_label = QLabel()
        # twitter_label.setText('🐦 <a href="https://twitter.com/HearingShef" style="text-decoration:none; color: #1DA1F2;">@HearingShef</a>')
        # twitter_label.setOpenExternalLinks(True)
        # twitter_label.setStyleSheet("""
        #     QLabel {
        #         color: #1DA1F2;  /* Twitter blue */
        #         font-size: 16px;
        #         font-weight: bold;
        #         padding: 8px;
        #         margin: 8px;
        #         border-radius: 15px;
        #     }
        #     QLabel:hover {
        #         background-color: #E8F5FE;
        #     }
        # """)

        # # Separator with style
        # separator = QLabel(" | ")
        # separator.setStyleSheet("color: #006064; font-size: 16px; margin: 0 10px;")

        # # Create website link with icon
        # website_label = QLabel()
        # website_label.setText('🎓 <a href="https://sheffield.ac.uk/hearing" style="text-decoration:none; color: #006064;">sheffield.ac.uk/hearing</a>')
        # website_label.setOpenExternalLinks(True)
        # website_label.setStyleSheet("""
        #     QLabel {
        #         color: #006064;
        #         font-size: 16px;
        #         font-weight: bold;
        #         padding: 8px;
        #         margin: 8px;
        #         border-radius: 15px;
        #     }
        #     QLabel:hover {
        #         background-color: #E0F7FA;
        #     }
        # """)

        # # Add labels to layout
        # contact_layout.addWidget(twitter_label)
        # contact_layout.addWidget(separator)
        # contact_layout.addWidget(website_label)
        # contact_layout.addStretch()
        
        # Remove logo section from header and create footer
        contact_layout = QHBoxLayout()
        main_layout.addLayout(contact_layout)

        # Add spacer to push content to bottom
        contact_layout.addStretch()

        # Create vertical layout for logo and uni name
        footer_logo_layout = QVBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.jpg")
        scaled_logo = logo_pixmap.scaled(100, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_logo)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("QLabel { padding: 5px; margin: 0px; background: transparent; }")

        uni_label = QLabel("University of Sheffield")
        uni_label.setAlignment(Qt.AlignCenter)
        uni_label.setStyleSheet("""
            QLabel {
                color: #006064;
                font-size: 14px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
            }
        """)

        footer_logo_layout.addWidget(logo_label)
        footer_logo_layout.addWidget(uni_label)
        footer_logo_layout.setSpacing(0)
        contact_layout.addLayout(footer_logo_layout)

        # Add separator
        separator = QLabel(" | ")
        separator.setStyleSheet("color: #006064; font-size: 16px; margin: 0 15px;")
        contact_layout.addWidget(separator)

        # Add Twitter and website links
        twitter_label = QLabel()
        twitter_label.setText('🐦 <a href="https://twitter.com/HearingShef" style="text-decoration:none; color: #1DA1F2;">@HearingShef</a>')
        twitter_label.setOpenExternalLinks(True)
        twitter_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }
        """)

        website_label = QLabel()
        website_label.setText('🎓 <a href="https://sheffield.ac.uk/hearing" style="text-decoration:none; color: #006064;">sheffield.ac.uk/hearing</a>')
        website_label.setOpenExternalLinks(True)
        website_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }
        """)

        contact_layout.addWidget(twitter_label)
        contact_layout.addWidget(website_label)
        contact_layout.addStretch()
        
        # Add welcome message at end of __init__
        self._show_welcome_message()

    def _show_welcome_message(self):
        """Display initial welcome message with streaming response"""
        self.message_history.append({
            "role": "assistant",
            "content": ""
        })
        self._update_chat_display()
        
        accumulated_response = ""
        introduction_prompt = f"Introduce yourself briefly as {DR_NAME}. Use two sentences max."
        for chunk in ollama.generate(
            **MODEL_CONFIG,
            prompt=introduction_prompt,
            stream=True
        ):
            accumulated_response += chunk['response']
            self.message_history[-1]["content"] = accumulated_response
            self._update_chat_display()
            QApplication.processEvents()

    def send_message(self):
        user_input = self.user_input.text()
        if not user_input.strip():
            return
            
        # Store user message
        self.message_history.append({"role": "user", "content": user_input})
        self.user_input.clear()
        
        # Stream response
        accumulated_response = ""
        self.message_history.append({"role": "assistant", "content": ""})
        
        for chunk in ollama.generate(
            **MODEL_CONFIG,
            prompt=self._get_conversation_history() + '\n' + user_input,
            stream=True
        ):
            accumulated_response += chunk['response']
            self.message_history[-1]["content"] = accumulated_response
            self._update_chat_display()
            QApplication.processEvents()

    def _get_conversation_history(self) -> str:
        """Get formatted conversation history for prompt"""
        formatted_msgs = []
        for msg in self.message_history:
            if msg["role"] == "system":
                formatted_msgs.append(msg["content"])
            else:
                formatted_msgs.append(f"{'You' if msg['role']=='user' else 'Bot'}: {msg['content']}")
        return "\n".join(formatted_msgs)

    def _update_chat_display(self):
        """Update chat display with formatted messages"""
        formatted_messages = []
        for msg in self.message_history:
            if msg["role"] == "system":
                continue  # Skip system messages in display
            if msg["role"] == "user":
                content = f'<div style="text-align: justify; line-height: 1.5;"><span style="color: red; font-size: 17px;">{msg["content"]}</span></div><br>'
                prefix = '<span style="color: red; font-size: 17px;">You: </span>'
            else:
                content = f'<div style="text-align: justify; line-height: 1.5;">{markdown.markdown(msg["content"])}</div><br>'
                prefix = f'<span style="color: black; font-size: 17px; font-weight: bold;">{DR_NAME}: </span>'
            formatted_messages.append(f"{prefix}{content}")
            
        self.chat_history.setHtml("""
            <div style="font-size: 16.5px; line-height: 1.5;">
                {messages}
            </div>
        """.format(messages="\n".join(formatted_messages)))
        
        max_scroll = self.chat_history.verticalScrollBar().maximum()
        self.chat_history.verticalScrollBar().setValue(int(max_scroll * 0.95))

    def send_personal_question(self):
        personal_question = self.personal_question_input.text()
        self.chat_history.append(f"You: {personal_question}")
        self.personal_question_input.clear()

        response = ollama.generate(
            **MODEL_CONFIG,
            prompt=self.chat_history.toPlainText()+'\n'+personal_question
        )['response']
        html = markdown.markdown(response)

        self.chat_history.append(html)

    def send_premade_question(self, question):
        self.user_input.setText(question)
        self.send_message()

def main():
    app = QApplication(sys.argv)
    window = ChatbotApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()