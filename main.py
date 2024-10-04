# PROFESSIONAL PROJECT: Recipe Data (Web Scraping and CSV file construction)
#
# Objectives:
# 1. To scrape a website containing recipe data and capture desired data elements.
# 2. To write captured data to a CSV file.

# Import necessary library(ies):
import collections  # Used for sorting items in the "selected recipes" dictionary
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from tkinter import *
from tkinter import filedialog, messagebox, ttk
import traceback

# Define constants for application default font size as well as window's height and width:
FONT_NAME = "Arial"
WINDOW_HEIGHT = 570
WINDOW_WIDTH = 510

# Define variable for the main GUI (application) window (so that it can be used globally), and make it a TKinter instance:
window = Tk()

# Withdraw the main application window from sight until it has been fully configured and ready for the user to interact with:
window.withdraw()

# Define variable for image to be displayed at top part of application window:
img = None

# Initiate a list variable which will store all available recipe types scraped from the recipe website:
combobox_recipe_type_values = []

# Initiate a variable which will store the recipe type selected by the user:
selected_recipe_type = StringVar()

# Initiate a dictionary variable which will store all available recipe names and links for a selected recipe type:
selected_recipes = {}

# Initiate a variables for storing the URL for the recipe website's main page:
url_recipe_site = "https://www.allrecipes.com/"


# DEFINE FUNCTIONS TO BE USED FOR THIS APPLICATION (LISTED IN ALPHABETICAL ORDER BY FUNCTION NAME):
def get_recipes():
    """Function used to scrape the recipe website and retrieve all recipes for the selected recipe type"""
    global selected_recipe_type, selected_recipes

    try:
        # Capture the selected recipe type:
        selected_recipe_type_scrape = selected_recipe_type.get()

        # Go to the recipe-type page on the website.  Return the Selenium driver initiated in same for further use in this function.
        # If an error occurs, return None (does not represent grounds for exiting this application):
        driver = go_to_recipe_type_page_on_website()
        if not driver:
            return None

        # Loop through all recipe types at the target website.  Search for the recipe type that the user has selected:
        additional_searching_needed = True    # Proceed with searching.
        i = 1   # Element-counter variable
        while additional_searching_needed:
            try:
                # Identify the xpath that leads to the element where the recipe type is referenced:
                xpath = '// *[ @ id = "mntl-link-list__item_' + str(i) + '-0"] / a'

                # Locate the element and assess if it pertains to the recipe type the user has selected:
                element = driver.find_element(By.XPATH, xpath)
                if element.text == selected_recipe_type_scrape:  # Element pertains to the user-selected recipe type
                    additional_searching_needed = False  # No more searching is needed.

                # Increment the element-counter variable by 1.
                i += 1

            except: # No more searching for the desired recipe type will be performed.
                additional_searching_needed = False

        # Click on the link pertaining to the chosen element.
        # This will lead to a page where all recipes for the selected recipe type are available:
        element.click()

        # Clear the recipe dictionary of its contents:
        selected_recipes.clear()

        # Loop through the recipe types at the target website.
        # Capture the name and link for each recipe pertaining to the user-selected recipe type:
        additional_searching_needed = True    # Proceed with searching.
        i = 1   # Element-counter variable
        error_count = 0
        while additional_searching_needed:
            try:
                # Identify the xpath that leads to the element for the current recipe's link (href):
                xpath = '// *[ @ id = "mntl-card-list-items_' + str(i) + '-0"]'

                # Locate the element.  Once found, capture the recipe's link:
                element = driver.find_element(By.XPATH, xpath)
                recipe_link = element.get_attribute('href')

                # Identify the xpath that leads to the element where the current recipe's name is referenced:
                xpath = '// *[ @ id = "mntl-card-list-items_' + str(i) + '-0"]/div[2]/span/span'

                # Locate the element.  Once found, capture the recipe's name and remove all commas from same:
                element = driver.find_element(By.XPATH, xpath)
                recipe_name = element.text.replace(',','')

                # Add the recipe's name and link to the "selected recipes" dictionary.
                # This dictionary will serve as the source of data to be written to the CSV file:
                selected_recipes.update({recipe_name: recipe_link})

                # Increment the element-counter variable by 1.
                i += 1

            except: # No more recipes are available.
                error_count += 1
                if error_count == 100:
                    additional_searching_needed = False

        # Close and delete the Selenium driver object:
        driver.close()
        del driver

        # Sort the selected recipes by recipe name:
        selected_recipes = collections.OrderedDict(sorted(selected_recipes.items()))

        # Write the results to a CSV file, giving user a choice of file name and location.
        # If an error occurs, return None (does not represent grounds for exiting this application):
        if not write_to_csv_file(selected_recipe_type_scrape):
            return None

    except:  # An error has occurred.
        # Inform user:
        messagebox.showinfo("Error", f"Error (get_recipes): {traceback.format_exc()}")

        # Update system log with error details:
        update_system_log("get_recipes", traceback.format_exc())

        # If Selenium driver object is open, close and destroy it:
        try:
            driver.close()
            del driver
        except:
            pass

        # Return None (does not represent grounds for exiting this application):
        return None


def get_recipe_types():
    """Function to scrape the recipe website, collect all recipe types from same, and add the recipe types to a list.  This list will feed the combo box on the main application window"""
    global combobox_recipe_type_values

    try:
        # Go to the recipe-type page on the website.  Return the Selenium driver initiated in same for further use in this function.
        # If an error occurs, return failed-execution indication to the calling function:
        driver = go_to_recipe_type_page_on_website()
        if not driver:
            return False

        # Loop through all recipe types at the target website:
        recipe_types_available = True    # Additional recipe types are presumed to be available for retrieval from the target URL.
        i = 1   # Element-counter variable
        while recipe_types_available:
            try:
                # Identify the xpath that leads to the element where the recipe type is referenced:
                xpath = '// *[ @ id = "mntl-link-list__item_' + str(i) + '-0"] / a'

                # Locate the element.  Once found, append it to the recipe-type list:
                element = driver.find_element(By.XPATH, xpath)
                combobox_recipe_type_values.append(element.text)

                # Increment the element-counter variable by 1.
                i += 1

            except: # No more recipe types are available.
                recipe_types_available = False

        # Close and delete the Selenium driver object:
        driver.close()
        del driver

        # Return successful-execution indication to the calling function:
        return True

    except:  # An error has occurred.
        # Inform user:
        messagebox.showinfo("Error", f"Error (get_recipe_types): {traceback.format_exc()}")

        # Update system log with error details:
        update_system_log("get_recipe_types", traceback.format_exc())

        # If Selenium driver object is open, close and destroy it:
        try:
            driver.close()
            del driver
        except:
            pass

        # Return failed-execution indication to the calling function:
        return False


def go_to_recipe_type_page_on_website():
    """Function for scraping the recipe website to access the recipe-type page of same"""
    try:
        # Initiate and configure a Selenium object which starts scraping at the website's main page.
        # If an error occurs, return failed-execution indication to the calling function:
        driver = setup_driver(url_recipe_site, 1600, 300)
        if not driver:
            return False

        # Find the element which, upon clicking, moves to the recipe-type page of the website:
        xpath = '//*[@id="mntl-header-nav_1-0"]/div[1]/ul/li[2]/a'
        element = driver.find_element(By.XPATH, xpath)
        element.click()

        # Return the Selenium driver object to the calling function:
        return driver

    except:  # An error has occurred.
        # Inform user:
        messagebox.showinfo("Error", f"Error (go_to_recipe_type_page_on_website): {traceback.format_exc()}")

        # Update system log with error details:
        update_system_log("go_to_recipe_type_page_on_website", traceback.format_exc())

        # If Selenium driver object is open, close and destroy it:
        try:
            driver.close()
            del driver
        except:
            pass

        # Return failed-execution indication to the calling function:
        return False


def handle_window_on_closing():
    """Function which confirms with user if s/he wishes to exit this application"""

    # Confirm with user if s/he wishes to exit this application:
    if messagebox.askokcancel("Exit?", "Do you want to exit this application?"):
        window.destroy()

        # Exit this application:
        exit()


def run_app():
    """Main function used to run this application"""
    try:
        # Inform user that retrieval of recipe types will commence:
        messagebox.showinfo("Get Recipe Types", f"Click on the OK button to begin retrieving the recipe types for you to select from.\n\nOnce you click on OK, please wait a brief moment and the main application window will appear.")

        # Scrape the recipe website and retrieve available recipe types.  This list of recipe types will feed the combo box
        # on the main application window.  If an error occurs, exit this application:
        if not get_recipe_types():
            exit()

        # Creates and configure all visible aspects of the main application window.  If an error
        # occurs, exit this application:
        if not window_config():
            exit()

        # Bring the main application window to sight so that the user can begin interacting with it:
        # window.attributes("-topmost", True)
        window.deiconify()

        # From this point, test will start and end based on user's use of the start/end button, with subsequent
        # functionality defined from there.

    except SystemExit:  # Exiting application.
        exit()

    except:  # An error has occurred.
        # Inform user:
        messagebox.showinfo("Error", f"Error (run_app): {traceback.format_exc()}")

        # Update system log with error details:
        update_system_log("run_app", traceback.format_exc())

        # If window object exists, destroy it:
        try:
            window.destroy()
        except:
            pass

        # Exit this application:
        exit()


def setup_driver(url, width, height):
    """Function for initiating and configuring a Selenium driver object"""
    try:
        # Keep Chrome browser open after program finishes:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)

        # Create and configure the Chrome driver (pass above options into the web driver):
        driver = webdriver.Chrome(options=chrome_options)

        # Access the desired URL.
        driver.get(url)

        # Set window position and dimensions, with the latter being large enough to display the website's elements needed:
        driver.set_window_position(0, 0)
        driver.set_window_size(width, height)

        # Return the Selenium driver object to the calling function:
        return driver

    except:  # An error has occurred.
        # Inform user:
        messagebox.showinfo("Error", f"Error (setup_driver): {traceback.format_exc()}")

        # Update system log with error details:
        update_system_log("setup_driver", traceback.format_exc())

        # If Selenium driver object is open, close and destroy it:
        try:
            driver.close()
            del driver
        except:
            pass

        # Return failed-execution indication to the calling function:
        return False


def update_system_log(activity, log):
    """Function to update the system log with errors encountered"""
    try:
        # Capture current date/time:
        current_date_time = datetime.now()
        current_date_time_file = current_date_time.strftime("%Y-%m-%d")

        # Update log file.  If log file does not exist, create it:
        with open("log_recipe_data_web_scraper_" + current_date_time_file + ".txt", "a") as f:
            f.write(datetime.now().strftime("%Y-%m-%d @ %I:%M %p") + ":\n")
            f.write(activity + ": " + log + "\n")

        # Close the log file:
        f.close()

    except:  # An error has occurred.
        messagebox.showinfo("Error", f"Error: System log could not be updated.\n{traceback.format_exc()}")


def window_center_screen():
    """Function which centers the application window on the computer screen"""
    try:
        # Capture the desired width and height for the window:
        w = WINDOW_WIDTH # width of tkinter window
        h = WINDOW_HEIGHT  # height of tkinter window

        # Capture the computer screen's width and height:
        screen_width = window.winfo_screenwidth()  # Width of the screen
        screen_height = window.winfo_screenheight()  # Height of the screen

        # Calculate starting X and Y coordinates for the application window:
        x = (screen_width / 2) - (w / 2)
        y = (screen_height / 2) - (h / 2)

        # Center the application window based on the aforementioned constructs:
        window.geometry('%dx%d+%d+%d' % (w, h, x, y))

        # Return successful-execution indication to the calling function:
        return True

    except:  # An error has occurred.
        # Inform user:
        messagebox.showinfo("Error", f"Error (window_center_screen): {traceback.format_exc()}")

        # Update system log with error details:
        update_system_log("window_center_screen", traceback.format_exc())

        # Return failed-execution indication to the calling function:
        return False


def window_config():
    """Function which creates and configures all visible aspects of the application window"""
    try:
        # Create and configure application window.  If an error occurs, return
        # failed-execution indication to the calling function:
        if not window_create_and_config():
            return False

        # Create and configure user interface.  If an error occurs, return failed-execution
        # indication to the calling function:
        if not window_create_and_config_user_interface():
            return False

        # Return successful-execution indication to the calling function:
        return True

    except:  # An error has occurred.
        # Inform user:
        messagebox.showinfo("Error", f"Error (window_config): {traceback.format_exc()}")

        # Update system log with error details:
        update_system_log("window_config", traceback.format_exc())

        # Return failed-execution indication to the calling function:
        return False


def window_create_and_config():
    """Function to create and configure the GUI (application) window"""
    global img

    try:
        # Create and configure the application window:
        window.title("My Recipe Retriever")
        window.minsize(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        window.config(padx=45, pady=0,bg='white')
        window.resizable(0, 0)  # Prevents window from being resized.
        window.attributes("-toolwindow", 1)  # Removes the minimize and maximize buttons from the application window.

        # Center the application window on the computer screen.  If an error occurs, return failed-execution
        # indication to the calling function:
        if not window_center_screen():
            return False

        # Prepare the application to handle the event of user attempting to close the application window:
        window.protocol("WM_DELETE_WINDOW", handle_window_on_closing)

        # Return successful-execution indication to the calling function:
        return True

    except:  # An error has occurred.
        # Inform user:
        messagebox.showinfo("Error", f"Error (window_create_and_config): {traceback.format_exc()}")

        # Update system log with error details:
        update_system_log("window_create_and_config", traceback.format_exc())

        # Return failed-execution indication to the calling function:
        return False


def window_create_and_config_user_interface():
    """Function which creates and configures items comprising the user interface, including the canvas (which overlays on top of the app. window), labels, combo box, and button"""
    global img

    try:
        # Create and configure canvas which overlays on top of window:
        canvas = Canvas(window)
        img = PhotoImage(file="yummy.png")
        canvas.config(height=img.height(), width=img.width(), bg='white', highlightthickness=0)
        canvas.create_image(40,40, image=img)
        canvas.grid(column=0, row=1, columnspan=3, padx=0, pady=0)
        canvas.update()

        # Create and configure the introductory header text (label):
        label_intro = Label(text=f"WELCOME TO MY RECIPE RETRIEVER!", height=3, bg='white', fg='black', padx=0, pady=0, font=(FONT_NAME,16, "bold"))
        label_intro.grid(column=0, row=0, columnspan=3)

        # Create and configure the header text (label) summarizing the objectives:
        objectives = f"Objectives of this application are as follows:\n\n1. To scrape a website containing recipe data\nand capture desired data elements.\n\n2. To write captured data to a CSV file.\n\nWebsite to be scraped: www.allrecipes.com"
        label_objectives = Label(text=objectives, height=6, bg='white', fg='blue', padx=0, pady=50, font=(FONT_NAME,14, "bold"), justify=LEFT)
        label_objectives.grid(column=0, row=2, columnspan=3)

        # Define a label for the recipe-type combo box:
        label_recipe_type = Label(text=f"SELECT RECIPE TYPE ({len(combobox_recipe_type_values)} types available):", bg='white', fg='red', padx=0, pady=5, font=(FONT_NAME,14, "bold"))
        label_recipe_type.grid(column=0, row=3, columnspan=3)

        # Create and configure a combo box to list recipe types:
        combobox_recipe_type = ttk.Combobox(window, height=10, width=25, font=(FONT_NAME,14, "normal"), state="readonly", values=combobox_recipe_type_values, textvariable=selected_recipe_type)
        combobox_recipe_type.grid(column=0, row=4, padx=0, pady=0, columnspan=3)

        # Create and configure the blank "label" which serves as a separator between the recipe combo box and the button:
        label_space = Label(text="", bg='white', fg='white', padx=0, pady=0, font=(FONT_NAME,16, "bold"))
        label_space.grid(column=0, row=5)

        # Create and configure button used to run the web scraper and subsequent functionality:
        button_scrape = Button(text="Get Recipes", width=12, height=1, bg='red', fg='white', pady=0, font=(FONT_NAME,16,"bold"), command=get_recipes)
        button_scrape.grid(column=0, row=6,columnspan=3)

        # Return successful-execution indication to the calling function:
        return True

    except:  # An error has occurred.
        # Inform user:
        messagebox.showinfo("Error", f"Error (window_create_and_config_user_interface): {traceback.format_exc()}")

        # Update system log with error details:
        update_system_log("window_create_and_config_user_interface", traceback.format_exc())

        # Return failed-execution indication to the calling function:
        return False


def write_to_csv_file(selected_recipe_type_scrape):
    """Function for archiving all recipes for a selected recipe type to a CSV file"""
    try:

        # Archive all recipes for the selected recipe types, using the contents of the "selected recipes" dictionary:
        file_path_identified = filedialog.asksaveasfilename(parent=window, initialfile="Recipes - " + selected_recipe_type_scrape,title="Save Recipes To File", defaultextension=".csv", filetypes=[("CSV file(*.csv)", "*.csv")])
        if file_path_identified:   # User has selected a file name and location.
            try:
                with open(file_path_identified, mode="w") as file:
                    # Write the column headers:
                    file.write("Recipe" + "," "URL" + "\n")

                    # Write each recipe's name and URL.  URL is written inside a "HYPERLINK" formula so that if the CSV file is
                    # opened in MS-Excel,the URL will be an active link that the user can click on to get to the desired recipe:
                    for recipe in selected_recipes:
                        file.write(recipe + "," + "=HYPERLINK(" + '"' + selected_recipes[recipe] + '"' + ")" + "\n")  # The character "," will be used as the delimiter.

                # Close the newly-created recipe CSV file:
                file.close()

                # Inform user that CSV file has been created:
                messagebox.showinfo("Recipe File Created", f"The following file has been created:\n\n{file_path_identified}")

            except Exception as err:  # Error has occurred.
                messagebox.showinfo("Error", f"{err}.\n\nFile has not been created.")

        else:  # User has not identified a file name and location to store the retrieved recipes.
            messagebox.showinfo("Recipe File Not Created", "File has not been created.")

        # Return successful-execution indication to the calling function:
        return True

    except:  # An error has occurred.
        # Inform user:
        messagebox.showinfo("Error", f"Error (write_to_csv_file): {traceback.format_exc()}")

        # Update system log with error details:
        update_system_log("write_to_csv_file", traceback.format_exc())

        # Return failed-execution indication to the calling function:
        return False


# Run the application:
run_app()

# Keep application window open until user closes it:
window.mainloop()

if __name__ == '__main__':
    run_app()