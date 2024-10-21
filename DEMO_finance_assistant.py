import openai
import streamlit as st
from dotenv import load_dotenv
import time
import re
import json
from os.path import basename
from openai import AssistantEventHandler
import os
from typing_extensions import override
from cryptography.fernet import Fernet
import firebase_admin
import base64
from firebase_admin import credentials, firestore



load_dotenv()


# Hidden Keys

encryption_key = st.secrets['ENCRYPTION_KEY_FIN']
cipher_suite = Fernet(encryption_key.encode())


OPENAI_API_KEY_dec= st.secrets['OPENAI_API_KEY_FIN']
VECTOR_STORE_ID_dec= st.secrets['VECTOR_STORE_ID_FIN']
ASSISTANT_ID_dec= st.secrets['ASSISTANT_ID_FIN']
SERVICE_ACCOUNT_dec= st.secrets['SERVICE_ACCOUNT_FIN']


encrypted_secrets= {
    'OPENAI_API_KEY': OPENAI_API_KEY_dec,
    'VECTOR_STORE_ID': VECTOR_STORE_ID_dec,
    'ASSISTANT_ID': ASSISTANT_ID_dec,
    'SERVICE_ACCOUNT': SERVICE_ACCOUNT_dec
    }


decrypted_secrets = {}

for key, value in encrypted_secrets.items():
    print(f"Decrypting {key}: {value}")
    decrypted_secrets[key] = cipher_suite.decrypt(value.encode()).decode()


OPENAI_API_KEY= decrypted_secrets['OPENAI_API_KEY'] 
VECTOR_STORE_ID= decrypted_secrets['VECTOR_STORE_ID']
ASSISTANT_ID= decrypted_secrets['ASSISTANT_ID']
SERVICE_ACCOUNT= decrypted_secrets['SERVICE_ACCOUNT']


if not SERVICE_ACCOUNT:
    raise ValueError("Base64-encoded service account key not found in environment variables.")

try:
    # Decode the Base64 string
    decoded_key = base64.b64decode(SERVICE_ACCOUNT).decode('utf-8')


    # Parse the JSON string into a dictionary
    service_account_info = json.loads(decoded_key)
    
    
except Exception as e:
    raise ValueError(f"Failed to load service account key: {e}")


# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred= credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred)

db= firestore.client()


openai.api_key = os.getenv('OPENAI_API_KEY_raw')
client = openai.OpenAI(api_key=openai.api_key)
model = "gpt-4o"
assis_id = os.getenv('ASSISTANT_ID_FIN')
vector_id = os.getenv('VECTOR_STORE_ID_FIN')



# # Upload Firebase Service Key
# path = "np-ai-agents-firebase.json"

# # Open the JSON file and read its contents
# with open(path, 'rb') as f:  # Open in binary mode to read bytes
#     key_bytes = f.read()  # Read the file contents as bytes

# # Convert the bytes to a Base64-encoded string
# base64_key = base64.b64encode(key_bytes).decode('utf-8')  # Encode to base64 and decode to a UTF-8 string

# # Print or store the Base64-encoded string
# print(base64_key)  # You can save this to an environment variable or file as needed


# while True:

#     time.sleep(1)


# # Vector Database Creation

# vector_finance= client.beta.vector_stores.create()

# print(vector_finance.id)

# while True:
#     time.sleep(1)



# # Update assistant

# instructions= """
# # Role:
# You are a financial analysis assistant for top-tier financial professionals and investment analysts. You are highly skilled in interpreting financial statements, including balance sheets, income statements, and cash flow statements. You have built-in functions that allow you to ingest and analyze data from various formats such as excel, pdf, and word. You are adept at pulling insights from the data, calculating financial ratios, and performing trend analysis based on the data provided by the user. You maintain a high level of professionalism, clarity, and conciseness in your responses.

# # Task:
# Your primary task is to assist financial professionals in analyzing assets, investments, and business financial statements. You use your expertise to calculate relevant financial ratios such as profitability, liquidity, and solvency ratios. You explain the significance of these ratios, offering interpretations based on patterns and trends you detect in the data. You can suggest additional financial metrics users might want to consider but you do not provide direct investment advice. Additionally, you offer clarification of financial terms and definitions for users when requested, ensuring they have a solid understanding of the analysis. You are thorough, professional, and precise in your feedback.

# # Specifics:
# Your expertise is relied upon for providing detailed, high-quality financial insights. You can calculate ratios such as Return on Equity (ROE), Current Ratio, Debt-to-Equity Ratio, and other important financial metrics. Your feedback must always reference the specific data provided by users and clearly indicate how the analysis is tied to that information. You explain the meaning of each ratio, how it was derived, and any key trends you identify. It is essential that you avoid giving any specific investment advice or recommendations, maintaining strict neutrality and focusing purely on analytical insights.

# # Context:
# You are used by financial professionals who are working on critical analyses of business assets, investments, and financial health. Your primary role is to support their decision-making processes by providing thorough analysis based on the financial data they submit. The accuracy, professionalism, and clarity of your analysis are essential because top-tier investment firms rely on the precision of your work. While you are highly knowledgeable and capable, you are restricted from offering any explicit investment advice, ensuring compliance with financial industry regulations.

# # Examples:
# ## Cashflow Analysis
# Q: Could you analyze the cash flow statement for this company?

# A: Absolutely! Before I proceed, could you provide a bit more context?

# Are you looking for insights into the company's operating cash flow performance, or would you prefer to focus on investment and financing activities?
# Could you also give me a brief overview of the company's main operations and industry?
# User Response: I'm focusing on their ability to cover liabilities using cash flow from operations. They're in manufacturing, so I want to see how efficiently they're using cash.

# A: Understood. I'll take a closer look at key cash flow ratios:

# Operating Cash Flow Ratio: 1.5
# CAPEX to Operating Cash Ratio: 0.45
# The Operating Cash Flow Ratio suggests that the company generates $1.50 from its core operations for every $1 of current liabilities, indicating strong liquidity. Meanwhile, the CAPEX to Operating Cash Ratio shows that 45% of the company's operating cash is reinvested into capital expenditures, which is a healthy sign of growth investment. Would you like to explore trends over the last few years or focus on this year's snapshot?

# ## Income Statement Analysis
# Q: I need an income statement analysis for this company.

# A: I can certainly assist with that! Could you clarify the type of analysis you're performing?

# Are you focusing on profitability or efficiency?
# Also, would you like a year-over-year trend analysis or a single-period snapshot?
# Finally, could you provide a brief overview of the company's main business operations?
# User Response: I'm analyzing their profitability, focusing on the most recent year. They're a retail company, so I'd like insight into profit margins.

# A: Great! Here's a breakdown of the key profitability ratios based on the most recent data:

# Gross Profit Margin: 30%
# Operating Profit Margin: 12%
# Net Profit Margin: 8%
# The Gross Profit Margin of 30% indicates that the company retains 30 cents for every dollar of sales after covering the cost of goods sold. This is fairly typical for the retail industry. The Operating Profit Margin of 12% suggests solid operational efficiency, though you may want to investigate if any one-off expenses impacted it. Finally, the Net Profit Margin of 8% indicates that after all expenses, the company retains $0.08 for each dollar of revenue, which is on par with industry averages. Would you like deeper insights into the impact of operating costs on profitability?

# ## Net Working Capital Analysis
# Q: Could you analyze the company's net working capital?

# A: Sure! Let's narrow down the analysis to best serve your needs:

# Are you primarily concerned with liquidity ratios like the Current Ratio or Quick Ratio, or are you focusing on how efficiently the company manages its assets, like Inventory Turnover?
# Could you briefly describe the client's core operations and industry?
# User Response: This is a tech company, so I'm more concerned with their Current Ratio and Receivables Days to understand liquidity and how quickly they’re collecting from customers.

# A: Based on your focus, here are the key metrics:

# Current Ratio: 1.7
# Accounts Receivable Days: 40 days
# Quick Ratio: 1.3
# The Current Ratio of 1.7 suggests the company has ample short-term assets to cover its liabilities. With Accounts Receivable Days at 40, it takes them about 40 days on average to collect payments from customers, which could indicate some inefficiencies depending on industry standards. The Quick Ratio of 1.3, which excludes inventory, shows that the company has solid liquidity even without relying on unsold products. Would you like to explore trends in these metrics over the past few periods or focus on the current state?

# ## Balance Sheet Analysis
# Q: Could you analyze the company's balance sheet?

# A: Of course! Let me clarify a few things:

# Are you interested in the company's leverage (like the Debt-to-Equity Ratio) or more in their solvency (like the Equity Ratio)?
# Also, are we looking at a single period or comparing trends over the years?
# Finally, could you share a quick overview of the client's business?
# User Response: This is a manufacturing company, and I'm particularly interested in their leverage. Let's look at a single period for now.

# A: Understood. Here are the key ratios based on the balance sheet data:

# Debt-to-Equity Ratio: 0.75
# Equity Ratio: 0.57
# The Debt-to-Equity Ratio of 0.75 means the company uses $0.75 of debt for every $1 of equity, which suggests moderate leverage. The Equity Ratio of 0.57 indicates that shareholders have a claim on 57% of the company's assets, with the remaining 43% financed by debt. Would you like to see how this compares to industry averages or trends over the past few years?

# ## Working Capital Days
# Q: Can you help me analyze the working capital days?

# A: Certainly! Could you clarify if you'd like me to focus on Inventory Turnover Days, Accounts Receivable Days, or both?

# Are we reviewing the business over a single year, or would you like me to spot trends?
# Also, could you provide a brief overview of the client's industry and business operations?
# User Response: I'm interested in both Inventory Turnover Days and Accounts Receivable Days for a manufacturing company, focusing on this year's performance.

# A: Here's the analysis:

# Inventory Turnover Days: 55 days
# Accounts Receivable Days: 38 days
# The Inventory Turnover Days indicate it takes the company 55 days on average to sell its stock, which may be typical for the manufacturing industry but should be compared to competitors. Meanwhile, Accounts Receivable Days of 38 show relatively fast collections, which is a positive sign for liquidity. Would you like to explore optimization opportunities in either of these areas?

# ## Summarizing Accounting Policy and Complex Treatments
# Q: Could you summarize the accounting policies and highlight any complex treatments?

# A: Absolutely! Could you provide some direction on which area you're most focused on?

# Are we examining revenue recognition, depreciation methods, or capital expenditures?
# Would you like a full overview or should I focus on specific complex treatments?
# User Response: Let's focus on Revenue Recognition and any complex policies for this company's long-term contracts.

# A: The company recognizes revenue based on the percentage-of-completion method for long-term contracts. This can be a complex treatment as it involves recognizing revenue in proportion to the completion of the contract rather than at the time of delivery. It's essential to closely monitor estimates of project completion to ensure revenue is reported accurately. Would you like me to investigate any other policies that might affect this accounting treatment?

# # Notes:
# When handling requests, confirm inputs with the user before running the analysis to ensure accuracy. Always reference the data the user has provided and display your calculations clearly, noting any trends or patterns observed. Maintain professional clarity, and never offer advice or recommendations on financial decisions to avoid compliance issues.

#     """

# list_tools= [{
#             "type": "function",
#             "function": {
#                 "name": "download_file",
#                 "description": "Assist users with exporting documents for copying they have drafted for their legal firm. The types of documents you will be exporting are contracts, agreements, letters and othe rlegal documents. You are to get the file data as inputs for this function",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "file_data":{"type": "string", "description": "Obtain the file data to be exported to be copied by users. Be sure to get the entire text no matter what the size of the information provided. This represents the data to be copied by users. Please be sure to incude the applicable formatting as per the draft."},
#                         },
#                         "required": ["file_data"],
#                     }
#                 }
#             },
#             {"type": "file_search"},
#             {"type": "code_interpreter"}
#         ]


# legal_ass= client.beta.assistants.create(
#     model= model,
#     name= "Corp_Fin_Assistant",
#     instructions= instructions,
#     temperature= 0.3,
#     tools= list_tools,
#     tool_resources={
#         "file_search":{
#             "vector_store_ids": [vector_id]
#         }
#     }
# )

# print(legal_ass.id)


# while True:
#     time.sleep(1)



def get_all_threads():
    try:
        threads = db.collection('threads_finance').stream()

        return [(thread.id, thread.to_dict().get('name', 'Untitled')) for thread in threads]
    
    except Exception as e:
        st.error(f"Error fetching threads: {e}")
        return []


def get_thread_name(thread_id):
    doc = db.collection('threads_finance').document(thread_id).get()
    if doc.exists:
        data = doc.to_dict()
        return data.get('name', 'Untitled')
    else:
        return 'Untitled'


def generate_thread_name(messages):

    global model

    # Concatenate user messages to form the conversation text
    conversation_text = "\n".join(
        [f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages]
    )
    
    # Use OpenAI API to summarize the conversation
    response = client.chat.completions.create(
        model='gpt-4o-mini',  # Use an appropriate model
        messages= [
            {"role":"system", "content":"Summarize the main topic of the following user conversations in a short phrase"},
            {"role":"user", "content":f"{conversation_text}"}
            ],
        max_tokens=10,
        temperature=0.5,
        n=1,
        stop=None,
    )

    summary = response.choices[0].message.content
    print(summary)
    return summary if summary else "Untitled"


def update_thread_name(thread_id, thread_name):

    db.collection('threads_finance').document(thread_id).update({'name': thread_name})


def save_thread(thread_id, messages, thread_name='Untitled'):

    try:
        thread_data= {
            'name': thread_name,
            'messages': messages,
        }

        # Saving thread messages to the database
        db.collection('threads_finance').document(thread_id).set(thread_data)

    except Exception as e:
        print(f"Error saving thread {thread_id}: {e}")


def load_thread(thread_id):

    doc= db.collection('threads_finance').document(thread_id).get()

    if doc.exists:
        data= doc.to_dict()

        return data.get('messages', [])
    else:
        return []


def create_new_thread():

    # Create a new thread using OpenAI API
    thread_create = client.beta.threads.create()
    thread_id_new = thread_create.id
    print(f"Created new thread: {thread_id_new}")

    # Initialize the conversation history for the new thread
    save_thread(thread_id_new, [], thread_name="Untitled")
    return thread_id_new


# Functions

def write_file(file):

    with open(f'{file.name}', 'wb') as f:
        f.write(file.getbuffer())

    return f'{file.name}'



# Export text file

def remove_file(file_path):

    time.sleep(1)
    os.remove(file_path)


def download_file(file_data):

    # Display Content
    st.sidebar.code(file_data, language='html')

    response= "File made available for export in the sidebar. Please click the copy putton to access your data"

    return response


# End Run
def end_chat():
    st.session_state.start_chat= False
    st.session_state.thread_id= None
    st.session_state.messages= []
    st.rerun()


def delete_thread(thread_id):

    client.beta.threads.delete(
        thread_id=thread_id
    )

    db.collection('threads_finance').document(thread_id).delete()

# Upload to OpenAI
def upload_openai(file_path, file_name):

    with open(file_path, "rb") as files:

        global thread_id

        message_file= client.files.create(
            file=files, purpose="assistants"
        )

        message= 'Upload the attached document to the thread database and wait for further instructions'

        upload_message= client.beta.threads.messages.create(
            thread_id= st.session_state.thread_id,
            role='user',
            content=message,
            attachments=[{"file_id":message_file.id,"tools":[{"type":"file_search"}]}]
        )

        time.sleep(2)

        print(upload_message.status)
        st.sidebar.success(f'File successfully uploaded to thread: {file_name}')

    if os.path.exists(file_path):
        os.remove(file_path)


list_tools= [{
            "type": "function",
            "function": {
                "name": "download_file",
                "description": "Assist users with exporting documents for copying they have drafted for their legal firm. The types of documents you will be exporting are contracts, agreements, letters and othe rlegal documents. You are to get the file data as inputs for this function",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_data":{"type": "string", "description": "Obtain the file data to be exported to be copied by users. Be sure to get the entire text no matter what the size of the information provided. This represents the data to be copied by users. Please be sure to incude the applicable formatting as per the draft."},
                        },
                        "required": ["file_data"],
                    }
                }
            },
            {"type": "file_search"}
        ]


class EventHandler(AssistantEventHandler):
    @override
    def on_event(self, event):
        # Retrieve events that are denoted with 'requires_action'
        # since these will have our tool_calls
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id
            self.handle_requires_action(event.data, run_id)


    def handle_requires_action(self, data, run_id):
        tool_outputs = []
        for tool in data.required_action.submit_tool_outputs.tool_calls:
            params_loaded = tool.function.arguments
            params = json.loads(params_loaded)
            print(f"Requested Tool: {tool.function.name}, Params: {params}")
            if isinstance(params, str):
                try:
                    params = json.loads(params)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
            elif tool.function.name == "download_file":
                file_data = download_file(**params)
                tool_outputs.append({"tool_call_id": tool.id, "output": f'{file_data}'})

        self.submit_tool_outputs(tool_outputs, run_id)


    def submit_tool_outputs(self, tool_outputs, run_id):

        # Use the submit_tool_outputs_stream helper
        with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()
            for text in stream.text_deltas:
                print(text, end="", flush=True)
            print()


# Start Run
def start_run(thread_id, assistant_id):
    try:
        with st.spinner('Typing...'):
            with client.beta.threads.runs.stream(
                thread_id=thread_id,
                assistant_id=assistant_id,
                event_handler=EventHandler()
            ) as stream:
                stream.until_done()
    except openai.BadRequestError as e:
        if 'already has an active run' in str(e):
            print("An active run is already in progress. Please wait for it to complete.")
        else:
            print(f"An error occurred: {e}")


def send_user_message(thread_id, content):
    user_message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )
    return user_message


def update_thread_name_after_message():

    if st.session_state.messages:
        thread_name= generate_thread_name(st.session_state.messages)
        update_thread_name(st.session_state.thread_id, thread_name)



# Fine-tune

def submit_fine_tune(thread_id, messages, thread_name):

    current_thread_name = get_thread_name(thread_name)

    try:

        thread_data= {
            'name': current_thread_name,
            'messages': messages,
        }

        # Saving thread messages to the database
        db.collection('fine-tuning_finance').document(thread_id).set(thread_data)

        
    except Exception as e:
        print(f"Error saving thread {thread_id}: {e}")

    success_message= "Succesfully submitted for fine-tuning"

    return success_message


# Streamlit Application
st.set_page_config(page_title="Finance Analysis Assistant", page_icon=":robot_face:")
st.title("Financial Analysis Assistant")
st.write("Interact with the financial analysis assistant for your business needs")


# Initialize session state variables if they don't exist
if 'confirm_end_chat' not in st.session_state:
    st.session_state.confirm_end_chat = False

if 'end_chat_success' not in st.session_state:
    st.session_state.end_chat_success = False


# Initialize session state variables
if 'start_chat' not in st.session_state:
    st.session_state.start_chat = False


if 'thread_id' not in st.session_state:
    st.session_state.thread_id = None


if 'messages' not in st.session_state:
    st.session_state.messages = []


# Sidebar - Thread selection
all_threads = get_all_threads()


if all_threads:

    # Reverse the list to have the latest threads at the top
    all_threads= all_threads[::-1]


    # Prepare options and mapping
    thread_options = [name if name else thread_id for thread_id, name in all_threads]
    thread_id_map = {name if name else thread_id: thread_id for thread_id, name in all_threads}


    # Determine the default index based on the current thread_id
    if st.session_state.thread_id in all_threads:
        current_name = get_thread_name(st.session_state.thread_id)
        default_index= all_threads.index(st.session_state.thread_id)

    else:
        default_index= 0 # Default to the latest thread

    selected_thread_name= st.sidebar.selectbox(
        "Select a conversation",
        thread_options,
        index= default_index
    )


    selected_thread_id = thread_id_map[selected_thread_name]


    if selected_thread_id != st.session_state.thread_id:
        st.session_state.thread_id = selected_thread_id
        st.session_state.messages = load_thread(selected_thread_id)
else:
    st.sidebar.write("No conversations yet.")
    st.session_state.thread_id= None
    st.session_state.messages=[]


# Buttons to manage chat sessions
if st.sidebar.button("New Chat"):
    st.session_state.start_chat = True
    st.session_state.thread_id = create_new_thread()  # Assuming create_new_thread returns thread_id
    st.session_state.messages = []

    # Save the new thread to Firestore
    save_thread(st.session_state.thread_id, st.session_state.messages, thread_name="Untitled")
    st.rerun()


if st.sidebar.button("End Chat"):

    # Set the confirmation flag
    st.session_state.confirm_end_chat = True


# Check if we are in the confirmation state
if st.session_state.confirm_end_chat:

    choice= st.sidebar.radio("Are you sure you want to end and delete this chat?", ("Select a Choice","Yes", "No"))


    if choice == "Yes":
        # Perform the action to end and delete the chat

        if st.session_state.messages:
            thread_name= generate_thread_name(st.session_state.messages)
            update_thread_name(st.session_state.thread_id, thread_name)
        
        else:
            thread_name= "Untitled"

        delete_thread(st.session_state.thread_id)
        st.session_state.start_chat = False
        st.session_state.thread_id = None
        st.session_state.messages = []
        st.session_state.confirm_end_chat = False  # Reset the confirmation flag
        st.session_state.end_chat_success = True  # Set success message flag
        st.rerun()

        st.sidebar.success("Chat has been ended and deleted.")


    elif choice == "No":
        st.sidebar.info("Chat not deleted.")
        st.session_state.confirm_end_chat = False  # Reset the confirmation flag
        

# Display success message if needed
if st.session_state.end_chat_success:
    st.sidebar.success("Chat has been ended and deleted.")
    st.session_state.end_chat_success = False  # Reset success message flag


# Sidebar file uploader
file_uploader = st.sidebar.file_uploader(
    "Upload any file below",
    accept_multiple_files=True,
    key=0
)


if st.sidebar.button("Upload File"):
    if file_uploader is not None:
        for file in file_uploader:
            file_name = os.path.basename(file.name)
            file_path = os.path.join(os.getcwd(), file_name)
            print(file_path)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            upload_openai(file_path, file_name)

    else:
        st.warning("No files selected for upload.")


# Start Chat
if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    st.session_state.thread_id = selected_thread_id
    st.session_state.messages = load_thread(selected_thread_id)


# Mark for Fine-Tuning
if st.sidebar.button("Fine-Tune"):
    
    submit_fine_tune(thread_id=st.session_state.thread_id, messages=st.session_state.messages, thread_name=st.session_state.thread_id)

    st.sidebar.warning("Conversation submitted for fine-tuning")


# Main chat interface
if st.session_state.start_chat and st.session_state.thread_id is not None:

    # Display existing messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for the user
    if prompt := st.chat_input("Enter text here..."):

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add user's message to session state and database
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_thread(st.session_state.thread_id, st.session_state.messages)

        # Send user's message to OpenAI API
        send_user_message(st.session_state.thread_id, prompt)
        start_run(st.session_state.thread_id, assis_id)

        # Retrieve assistant's response
        assis_messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        # Find the latest assistant message
        assistant_message = None
        for msg in assis_messages.data:
            if msg.role == 'assistant':
                assistant_message = msg
                break
        if assistant_message:
            final_response = assistant_message.content[0].text.value
            final_clean = re.sub(r'【\d+:\d+†.*?】', '', final_response)

            # Display assistant's message
            with st.chat_message("assistant"):
                st.markdown(final_clean)

            # Add assistant's message to session state and database
            st.session_state.messages.append(
                {"role": "assistant", "content": final_clean}
            )


            # Update thread name based on the conversation
            update_thread_name_after_message()  # Function that updates the thread name

            # Save updated messages to Firestore
            save_thread(st.session_state.thread_id, st.session_state.messages, get_thread_name(st.session_state.thread_id))
else:
    st.write("Please start a chat to begin.")

