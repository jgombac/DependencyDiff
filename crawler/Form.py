from Element import Element


class Form(Element):

    def __init__(self, browser, form):
        super(Form, self).__init__(browser, form)
        self.children = map(lambda x: Element(self.browser, x), self.browser.find_elements_by_xpath(self.xpath + "//*"))


    def fill(self):
        for child in self.children:
            self.fill_element(child)


    def fill_element(self, element: Element):
        tag = element().tag_name
        if tag == "input":
            type = element().get_attribute("type")
            if type == "text":
                element().send_keys("test")
            if type == "email":
                element().send_keys("test.email@mail.com")
            if type == "button":
                pass
            if type == "checkbox":
                pass
            if type == "color":
                pass
            if type == "date":
                pass
            if type == "datetime-local":
                pass
            if type == "file":
                pass
            if type == "hidden":
                pass
            if type == "image":
                pass
            if type == "month":
                pass
            if type == "number":
                pass
            if type == "password":
                pass
            if type == "radio":
                pass
            if type == "range":
                pass
            if type == "reset":
                pass
            if type == "search":
                pass
            if type == "submit":
                pass
            if type == "tel":
                pass
            if type == "text":
                pass
            if type == "time":
                pass
            if type == "url":
                pass
            if type == "week":
                pass

        if tag == "select":
            pass
            # TODO add all scenarios

    def submit(self):
        self.browser.execute_script("arguments[0].submit();", self.__ele())


