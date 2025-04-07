EMAIL_SAMPLES = [
    {
    #Ignore email example; mass company announcement
        "author": "Alice Jones <alice.jones@bar.com>",
        "to": "Anamay Deshpande <anamay.deshpande@company.com>",
        "subject": "Xmas Party Theme", 
        "email_thread": "Hi Team,\n\nLetting you know that our annual Christmas party is coming up. \
            The theme is Xmas Movies.\n\nBest,\nAlice"
    },

    {
    #Notify email example; project status update
        "author": "Alice Jones <alice.jones@company.com>",
        "to": "Anamay Deshpande <anamay.deshpande@company.com>",
        "subject": "Project Update", 
        "email_thread": "Hi Team,\n\nLetting you know that the billing dashboard project is now live. \
            Kudos to the team for delivering on time! @Monitoring team, please inform if any critical issues arise.\\n\nBest,\nAlice"
    },

    {
    #Respond email example; direct question from team member
        "author": "Alice Jones <alice.jones@bar.com>",
        "to": "Anamay Deshpande <anamay.deshpande@company.com>",
        "subject": "Quick question about API documentation",
        "email_thread": "Hi Anamay,\n\nUrgent issue - your service is down. Is there a reason why"
    }
]

def get_email_input(index=0):
    """Retrieve an email input by index from the sample list."""
    if 0 <= index < len(EMAIL_SAMPLES):
        return EMAIL_SAMPLES[index]
    raise ValueError(f"Email index {index} out of range. Valid range: 0 to {len(EMAIL_SAMPLES) - 1}")