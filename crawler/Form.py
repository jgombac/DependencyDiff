from Element import Element


class Form(Element):

    def __init__(self, browser, form):
        super(Form, self).__init__(browser, form)
        self.children = map(lambda x: Element(self.browser, x), self.browser.find_elements_by_xpath(self.xpath + "//*"))


    def fill(self, definition):
        print("filling form", self.xpath)
        for child in self.children:
            self.fill_element(child, definition)


    def fill_element(self, element: Element, definition):
        try:
            value = ""
            if definition:
                value = definition["elements"].get(element.xpath)
            tag = element().tag_name
            if tag == "input":
                type = element().get_attribute("type")
                print("filling element", element.xpath, tag, type)
                if type == "text":
                    element().send_keys(value if value else "testna@vrednost.com")
                if type == "email":
                    element().send_keys(value if value else "test.email@mail.com")
                if type == "password":
                    element().send_keys(value if value else "TestPassword123")
                # if type == "button":
                #     pass
                # if type == "checkbox":
                #     pass
                # if type == "color":
                #     pass
                # if type == "date":
                #     pass
                # if type == "datetime-local":
                #     pass
                # if type == "file":
                #     pass
                # if type == "hidden":
                #     pass
                # if type == "image":
                #     pass
                # if type == "month":
                #     pass
                # if type == "number":
                #     pass
                # if type == "radio":
                #     pass
                # if type == "range":
                #     pass
                # if type == "reset":
                #     pass
                # if type == "search":
                #     pass
                # if type == "submit":
                #     pass
                # if type == "tel":
                #     pass
                # if type == "text":
                #     pass
                # if type == "time":
                #     pass
                # if type == "url":
                #     pass
                # if type == "week":
                #     pass

            # if tag == "select":
            #     pass
                # TODO add all scenarios
            return True
        except Exception as ex:
            print("Failed to fill element:", self.xpath, element.xpath, ex)
            return False


    def submit(self):
        try:
            script = """
            var sub = arguments[0].querySelector('[type=\"submit\"]');
            if (sub != null) { sub.click() }
            else { arguments[0].submit(); }
            """
            self.browser.execute_script(script, self.get_element())
            return True
        except Exception as ex:
            print("Failed to submit form:", self.xpath, ex)
            return False


