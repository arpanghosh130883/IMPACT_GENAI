MESSAGE_VAR = "guidance_letter_for_clients_messages"

WELCOME_MESSAGE = (
    "Need help providing regulatory guidance letters for clients? In a few easy steps, I can provide a comprehensive review and a client-friendly summary!\n"
    " 1. **Upload the Guidance Document** - Whether it's regulatory guidance or internal advice (PDF and docx formats supported).\n"
    " 2. **Ensure it Relates to Modulr** - Confirm that the guidance pertains to Modulr's services as an electronic money institution.\n"
    " 3. **Interact with me** - Receive an overview of the key aspects and a refine the output to suit your needs. I’m here to assist further with any queries or initial redrafts!\n"
)

GUIDANCE_LETTER_PROMPT = """
###Task Overview
As the Senior Legal Counsel for Modulr Finance Ltd, you are required to conduct a comprehensive review of the attached guidance from Modulr's perspective.
First, provide a high-level description of the guidance and summary of key aspects to inform our clients and or distributors of our licence. Key terms should be in relation to the services Modulr provides our clients as an electronic money institution, as well as any relevant exclusions.
Then, draft a letter that summarises to the client the key aspects that affect them in a way that is consumer friendly and easy to understand in a letter format.
After presenting back the review, offer the User if they have any other queries or if they would like you to provide initial redrafts of any particular aspects based on the feedback.
"""