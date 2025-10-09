from flask import render_template

def render_message(headerText, bodyText, buttonText, buttonRedirect):
    """
    Prepares a message.html template with the given parameters.
    
    Args:
        headerText (str): The header text of the message
        bodyText (str): The body of the message
        buttonText (str): The text to display on the button
        buttonRedirect (str): URL to redirect when the button is clicked
    """
    return render_template('message.html', 
        headerText=headerText, 
        bodyText=bodyText,
        buttonText=buttonText,
        buttonRedirect=buttonRedirect)
