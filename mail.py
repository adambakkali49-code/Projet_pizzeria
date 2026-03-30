import os


def write_mail_to_file(recipient, subject, body):
    os.makedirs("mails", exist_ok=True)

    filename = f"mails/mail_{recipient.replace('@', '_').replace('.', '_')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"To: {recipient}\n")
        f.write(f"Subject: {subject}\n\n")
        f.write(body)

    print(f"Mail sauvegardé dans {filename}")