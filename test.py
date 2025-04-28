from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.service import Service
import random

def generate_random_message():
    words = ["Hello", "How", "Are", "You", "Today", "Python", "Random", "Message", "Generator", "apple", "banana", "cat"]
    message = ' '.join(random.sample(words, k=random.randint(3, 5)))
    return message

if __name__ == '__main__':
# ----------- generate random content for testing  ---------------
    random_number = random.randint(100, 998)
    test_username = "test"+str(random_number)
    test_email = test_username+"@gmail.com"
    test_old_password = test_username
    test_new_password = "test"+str(random_number+1)
    test_msg1 = generate_random_message()
    test_msg2 = generate_random_message()

    service = Service(executable_path='./chromedriver')
    driver = webdriver.Chrome(service=service)
    driver.get("http://127.0.0.1:8000")

# ----------- sign up ---------------
    firstname = driver.find_element(by=By.ID,value="First_Name")
    familyname = driver.find_element(by=By.ID,value="Family_Name")
    gender = driver.find_element(by=By.ID,value="Gender")
    city = driver.find_element(by=By.ID,value="City")
    country = driver.find_element(by=By.ID,value="Country")
    email = driver.find_element(by=By.ID,value="SignUpEmail")
    password = driver.find_element(by=By.ID,value="SignUpPassword")
    repeatpassword = driver.find_element(by=By.ID,value="SignUpPassword_Re")
    submit_signup   = driver.find_element(by=By.ID,value="submit_signup")

    firstname.send_keys(test_username)
    familyname.send_keys("Yang")
    gender.send_keys("man")
    city.send_keys("Linkoping")
    country.send_keys("Sweden")
    email.send_keys(test_email)
    password.send_keys(test_old_password)
    repeatpassword.send_keys(test_old_password)
    submit_signup.click()
    sleep(3)

    usermail = driver.find_element(by=By.ID,value="user_info_email")
    userfirstname = driver.find_element(by=By.ID,value="user_info_firstname")
    userfamilyname = driver.find_element(by=By.ID,value="user_info_familyname")
    usergender = driver.find_element(by=By.ID,value="user_info_gender")
    usercity = driver.find_element(by=By.ID,value="user_info_city")
    usercountry = driver.find_element(by=By.ID,value="user_info_country")

    assert usermail.is_displayed()
    assert usermail.text==test_email
    assert userfirstname.text==test_username
    assert userfamilyname.text=="Yang"
    assert usergender.text=="man"
    assert usercity.text=="Linkoping"
    assert usercountry.text=="Sweden"
    
    signout_button   = driver.find_element(by=By.ID,value="signout")
    signout_button.click()
    sleep(3)
    print("finish test sign_up")

# ----------- sign in ---------------
    email = driver.find_element(by=By.ID,value="SignInEmail")
    password = driver.find_element(by=By.ID,value="SignInPassword")
    submit_signin   = driver.find_element(by=By.ID,value="submit_signin")
    
    email.send_keys(test_email)
    password.send_keys(test_old_password)
    submit_signin.click()
    sleep(3)
    
    usermail = driver.find_element(by=By.ID,value="user_info_email")
    userfirstname = driver.find_element(by=By.ID,value="user_info_firstname")
    userfamilyname = driver.find_element(by=By.ID,value="user_info_familyname")
    usergender = driver.find_element(by=By.ID,value="user_info_gender")
    usercity = driver.find_element(by=By.ID,value="user_info_city")
    usercountry = driver.find_element(by=By.ID,value="user_info_country")

    assert usermail.is_displayed()
    assert usermail.text==test_email
    assert userfirstname.text==test_username
    assert userfamilyname.text=="Yang"
    assert usergender.text=="man"
    assert usercity.text=="Linkoping"
    assert usercountry.text=="Sweden"
    print("finish test sign_in")

# ----------- post message ---------------
    message = driver.find_element(by=By.ID,value="home_tab_text")
    message.send_keys(test_msg1)
    submit_post=driver.find_element(by=By.ID,value="home_post_button")
    submit_post.click()
    sleep(5)
    msg_wall = driver.find_element(By.ID, "msg_wall").get_attribute('innerHTML')
    assert "from: "+test_email in msg_wall
    assert test_msg1 in msg_wall
    print("finish test post_msg")

# ----------- browse other info ---------------
    browse_tab = driver.find_element(by=By.ID,value="browse_tab")
    browse_tab.click()
    email = driver.find_element(by=By.ID,value="browse_email")
    submit = driver.find_element(by=By.ID,value="submit_browse")
    email.send_keys("test1@gmail.com")
    submit.click()
    sleep(3)

    usermail = driver.find_element(by=By.ID,value="other_user_info_email")
    userfirstname = driver.find_element(by=By.ID,value="other_user_info_firstname")
    userfamilyname = driver.find_element(by=By.ID,value="other_user_info_familyname")
    usergender = driver.find_element(by=By.ID,value="other_user_info_gender")
    usercity = driver.find_element(by=By.ID,value="other_user_info_city")
    usercountry = driver.find_element(by=By.ID,value="other_user_info_country")

    assert usermail.is_displayed()
    assert usermail.text=="test1@gmail.com"
    assert userfirstname.text=="1"
    assert userfamilyname.text=="1"
    assert usergender.text=="man"
    assert usercity.text=="1"
    assert usercountry.text=="1"   
    print("finish test browse_other_info")

# ----------- post other message ---------------
    message   = driver.find_element(by=By.ID,value="browse_tab_text")
    message.send_keys(test_msg2)
    submit_post=driver.find_element(by=By.ID,value="browse_post_button")
    submit_post.click()
    sleep(5)

    submit_reload=driver.find_element(by=By.ID,value="browse_reload_button")
    submit_reload.click()
    sleep(3)

    other_msg_wall_content = driver.find_element(By.ID, "other_msg_wall").get_attribute('innerHTML')
    assert "from: "+test_email in other_msg_wall_content
    assert test_msg2 in other_msg_wall_content
    print("fininsh post_other_msg")

# ----------- change password ---------------
    account_tab = driver.find_element(by=By.ID,value="account_tab")
    account_tab.click()
    sleep(1)

    old_password = driver.find_element(by=By.ID,value="change_old_passwd")
    new_password = driver.find_element(by=By.ID,value="change_new_passwd")
    repeat_new_password = driver.find_element(by=By.ID,value="change_new_passwd_re")
    submit_changePW = driver.find_element(by=By.ID,value="submit_changePW")
    old_password.send_keys(test_old_password)
    new_password.send_keys(test_new_password)
    repeat_new_password.send_keys(test_new_password)
    submit_changePW.click()
    sleep(3)

    signout = driver.find_element(by=By.ID,value="signout")
    signout.click()
    sleep(1)

    email = driver.find_element(by=By.ID,value="SignInEmail")
    password = driver.find_element(by=By.ID,value="SignInPassword")
    submit_signin = driver.find_element(by=By.ID,value="submit_signin")
    email.send_keys(test_email)
    password.send_keys(test_new_password)
    submit_signin.click()    
    sleep(3)

    usermail = driver.find_element(by=By.ID,value="user_info_email")
    userfirstname = driver.find_element(by=By.ID,value="user_info_firstname")
    
    assert usermail.is_displayed()
    assert usermail.text==test_email
    assert userfirstname.text==test_username
    print("finish test change_password")
    driver.close()