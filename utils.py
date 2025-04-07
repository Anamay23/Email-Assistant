#def parse_email(email_input: dict) -> dict:
def parse_email(email_input: dict) -> tuple[str, str, str, str]:
    """Parse an email input dictionary.

    Args:
        email_input (dict): Dictionary containing email fields:
            - author: Sender's name and email
            - to: Recipient's name and email
            - subject: Email subject line
            - email_thread: Full email content

    Returns:
        tuple[str, str, str, str]: Tuple containing:
            - author: Sender's name and email
            - to: Recipient's name and email
            - subject: Email subject line
            - email_thread: Full email content
    """
    return (
        email_input["author"],
        email_input["to"],
        email_input["subject"],
        email_input["email_thread"],
    )

def format_few_shot_examples(examples):
    """Format examples into a readable string representation for triage prompts.

    Args:
        examples: List of example items from the store, each with a value dict containing
            'email' (dict with author, to, subject, email_thread) and 'label' (str).

    Returns:
        str: A formatted string with examples separated by dashed lines.
    """

    template = """Email Subject: {subject}
Email From: {from_email}
Email To: {to_email}
Email Content: 
```
{content}
```
> Triage Result: {result}"""

    strs = ["Here are some previous examples:"]
    for eg in examples:
        strs.append(
            template.format(
                subject=eg.value["email"]["subject"],
                to_email=eg.value["email"]["to"],
                from_email=eg.value["email"]["author"],
                content=eg.value["email"]["email_thread"][:500],
                result=eg.value["label"],
            )
        )
    return "\n\n------------\n\n".join(strs)



# Use this definition of format_few_shot_examples in next versions, when you want to store 
# the original classification and the correct classification as well (to improve model performance)

#def format_few_shot_examples(examples):
#    """Format examples into a readable string representation.

#    Args:
#        examples (List[Item]): List of example items from the vector store, where each item
#            contains a value string with the format:
#            'Email: {...} Original routing: {...} Correct routing: {...}'

#    Returns:
#        str: A formatted string containing all examples, with each example formatted as:
#            Example:
#            Email: {email_details}
#            Original Classification: {original_routing}
#            Correct Classification: {correct_routing}
#           ---
#    """
#    formatted = []
#    for example in examples:
#        # Parse the example value string into components
#        email_part = example.value.split('Original routing:')[0].strip()
#        original_routing = example.value.split('Original routing:')[1].split('Correct routing:')[0].strip()
#        correct_routing = example.value.split('Correct routing:')[1].strip()
#        
        # Format into clean string
#        formatted_example = f"""Example:
#Email: {email_part}
#Original Classification: {original_routing}
#Correct Classification: {correct_routing}
#---"""
#        formatted.append(formatted_example)
    
#    return "\n".join(formatted)
