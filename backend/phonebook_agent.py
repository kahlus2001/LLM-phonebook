import os
from langchain.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import SystemMessagePromptTemplate
from langchain_openai import ChatOpenAI

from pydantic import BaseModel, Field
from models import Session

from agent_tools import create_contact, delete_contact, update_contact, get_contact, list_contacts, rename_contact


SYSTEM_PROMPT = """
You are a helpful digital assistant for managing a phonebook application.

You **never** invent or guess contact data; you only perform operations by selecting the appropriate tool. You always respond with accurate results based on the database and never hallucinate contact information.

## Tools Available

You can select from these tools, each requiring the specified input:
- `create_contact`: Add a new contact. Requires both "name" (string) and "phone" (string).
- `delete_contact`: Delete an existing contact. Requires "name" (string).
- `update_contact`: Update the phone number of an existing contact. Requires both "name" (string) and "phone" (string).
- `get_contact`: Retrieve a specific contact's phone number. Requires "name" (string).
- `list_contacts`: Retrieve a list of all contacts in the phonebook. Takes no arguments.
- `rename_contact`: Change the name of an existing contact. Requires both "old_name" and "new_name" (strings).

## Input Conventions

- When calling a tool, always provide arguments as a **JSON object** with the required keys.  
  For example:
    - To add a contact: `{"name": "Alice", "phone": "123456789"}`
    - To get a contact: `{"name": "Alice"}`
    - To rename a contact, use: {"old_name": "Patrycja Evans", "new_name": "Patrycja Michelli"}
- Never invent or assume data not present in the phonebook.
- If information is missing from the user request, always ask for clarification.
- Never attempt to synthesize contact or phone number information.

## Output Format

The **result of every action** is always returned as a JSON object with these two fields:
- `"message"`: (string) — A user-friendly status or answer, such as "Added contact Alice." or "Alice's phone number is 123456789."
- `"contacts"`: (list of objects) — A list of contacts in the form `[{"name": "...", "phone": "..."}]`. This list is:
    - Populated with relevant contact(s) if appropriate (e.g., `get_contact`, `list_contacts`, `create_contact` returns the new contact, etc.)
    - An empty list if no contact data needs to be shown (e.g., after deletion or when not found).

**You must always return both fields, even if one is empty.** Example outputs:
- Creating a contact: `{"message": "Added contact Alice.", "contacts": [{"name": "Alice", "phone": "123456789"}]}`
- Listing contacts: `{"message": "Here are all your contacts.", "contacts": [{"name": "Alice", "phone": "123456789"}, {"name": "Bob", "phone": "987654321"}]}`
- Deleting: `{"message": "Deleted contact Alice.", "contacts": [{"name": "Alice", "phone": "123456789"}]}`
- Not found: `{"message": "Contact Carol not found.", "contacts": []}`

## Instructions

- Carefully interpret the user's request and select only one tool per request.
- If a request cannot be completed (missing arguments, unknown contact, etc.), provide an appropriate message and an empty contact list.
- Never answer directly; always call a tool and return its output as the user’s answer.
- All responses must be in the strict JSON structure described above.
"""

def tool_create_contact(name: str, phone: str) -> str:
    """Create a new contact. Requires both 'name' and 'phone' as strings."""
    with Session() as session:
        return create_contact(session, name, phone)

def tool_delete_contact(name: str) -> str:
    """Delete a contact by name. Requires 'name' as a string."""
    with Session() as session:
        return delete_contact(session, name)

def tool_update_contact(name: str, phone: str) -> str:
    """Update a contact's phone number. Requires both 'name' and 'phone' as strings."""
    with Session() as session:
        return update_contact(session, name, phone)

def tool_get_contact(name: str) -> str:
    """Get a contact's phone number by name. Requires 'name' as a string."""
    with Session() as session:
        return get_contact(session, name)
    
def tool_list_contacts() -> list:
    with Session() as session:
        return list_contacts(session)
    
def tool_rename_contact(old_name: str, new_name: str) -> str:
    """Rename a contact. Requires both 'old_name' and 'new_name' as strings."""
    with Session() as session:
        return rename_contact(session, old_name, new_name)
    

class ContactInput(BaseModel):
    name: str = Field(..., description="The contact's name")
    phone: str = Field(..., description="The contact's phone number")

class NameInput(BaseModel):
    name: str = Field(..., description="The contact's name")

class EmptyInput(BaseModel):
    pass

class RenameContactInput(BaseModel):
    old_name: str = Field(..., description="The current name of the contact to rename")
    new_name: str = Field(..., description="The new name for the contact")


tools = [
    StructuredTool.from_function(
        name="create_contact",
        description=(
            "Add a new contact to the phonebook. "
            "Input must be a JSON object with both 'name' (string) and 'phone' (string), e.g. "
            '{"name": "Alice", "phone": "123456789"}'
        ),
        func=tool_create_contact,
        args_schema=ContactInput,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="delete_contact",
        description=(
            "Delete a contact from the phonebook. "
            "Input must be a JSON object with 'name' (string), e.g. "
            '{"name": "Alice"}'
        ),
        func=tool_delete_contact,
        args_schema=NameInput,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="update_contact",
        description=(
            "Update a contact's phone number. "
            "Input must be a JSON object with both 'name' (string) and 'phone' (string), e.g. "
            '{"name": "Alice", "phone": "987654321"}'
        ),
        func=tool_update_contact,
        args_schema=ContactInput,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="get_contact",
        description=(
            "Retrieve a contact's phone number. "
            "Input must be a JSON object with 'name' (string), e.g. "
            '{"name": "Alice"}'
        ),
        func=tool_get_contact,
        args_schema=NameInput,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="list_contacts",
        description="List all contacts in the phonebook. Returns a JSON array of objects with 'name' and 'phone'.",
        func=tool_list_contacts,
        args_schema=EmptyInput,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="rename_contact",
        description=(
            "Rename an existing contact. "
            "Input must be a JSON object with both 'old_name' and 'new_name' (strings), e.g. "
            '{"old_name": "Patrycja Evans", "new_name": "Patrycja Michelli"}'
        ),
        func=tool_rename_contact,
        args_schema=RenameContactInput,
        return_direct=True,
    )   
]

llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    model="gpt-3.5-turbo-1106"
)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    system_message=SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)
)