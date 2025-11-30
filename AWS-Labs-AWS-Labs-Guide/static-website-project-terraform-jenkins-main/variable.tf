variable "my_ami" {
  default = "ami-02b8269d5e85954ef"
}

variable "my_instance" {
  default = "t2.micro"
}

variable "my_key" {
  default = "Jenkins"
}
variable "user_data" {
   type = string
}