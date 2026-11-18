'''
License textMIT Licensehttps://mit-license.org/Copyright © 2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''
import random
import string
import secrets
from faker import Faker
from xeger import Xeger
x = Xeger()
import secrets
faker = Faker()

class FakeData:
    @staticmethod
    def person():
        return faker.name()
    
    @staticmethod
    def email_address():
        return faker.email()

    @staticmethod
    def us_ssn():
        return faker.ssn()
    
    @staticmethod   
    def address():
        return faker.address()
    @staticmethod
    def date_time():
        return faker.date()
    @staticmethod
    def location():
        return faker.city()
    
    @staticmethod
    def credit_card():
        return faker.credit_card_number()
    @staticmethod
    def crypto():
        return faker.cryptocurrency_name()
    @staticmethod
    def date():
        return faker.date()
    @staticmethod
    def ip_address():
        return faker.ipv4()
    @staticmethod
    def phone_number():
        return faker.phone_number()
    
    # def AADHAR_NUMBER():
    #     fake=Faker()
    #     aadhaar_number = fake.random_int(min=100000000000, max=999999999999)  # Generate a 12-digit random number
    #     aadhaar_number = str(aadhaar_number)  # Convert the number to a string
    #     aadhaar_number_with_space = ' '.join(aadhaar_number[i:i+4] for i in range(0, len(aadhaar_number), 4))
    #     return aadhaar_number_with_space


    # def PAN_Number():
    #     p="[A-Z]{5}[0-9]{4}[A-Z]{1}"
    #     t=x.xeger(p)
    #     print(t)
        
    #     return t
    @staticmethod
    def iban_code():
        return faker.iban()
    @staticmethod
    def passport():
        # print("faker.passport_number()",faker.passport_number())
        return faker.passport_number()

    @staticmethod
    def data_list(data,text):
        random_data=secrets.choice([item for item in data if str(item).lower() != text.lower()])
        return random_data

    

# class FakeDataList:

#     def 