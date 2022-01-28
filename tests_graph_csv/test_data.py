mock_data = ['Courtney', 'Raphael', 'Tammy', 'Michelle', 'Thomas', 'Bobby', 'Scott', 'Robert', 'Mary', 'Loretta', 'Stephen', 'Brandi', 'Mark', 'James', 'Patricia', 'Joseph', 'Carrie', 'Teresa', 'John', 'Charles', 'Larry', 'Ruby', 'Donna', 'Damon', 'Matthew', 'Kelly', 'Richard', 'David', 'Jonathan', 'Heather', 'Lori', 'Harold', 'Jo', 'Frankie', 'Tanya', 'Deborah', 'Sabrina', 'Erin', 'Wilfredo', 'Raymond', 'Norma', 'Maria', 'Dorothy', 'Benjamin', 'Marion', 'Leah', 'Timothy', 'Antonio', 'Nicki', 'Velma', 'Gary', 'Randy', 'Margaret', 'Jason', 'Roger', 'Michael', 'Brent', 'Lenore', 'Holly', 'Chana', 'Barbara', 'Terrence', 'Ashton', 'Renata', 'Eugene', 'Juanita', 'William', 'Serina', 'Joanna', 'Ann', 'Lisa', 'Emmett', 'Silvia', 'Wanda', 'Diane', 'Dian', 'Jerome', 'Priscilla', 'Ronald', 'Alicia', 'Bette', 'Bradley', 'Brad', 'Araceli', 'Kevin', 'Jeffrey', 'Alfred', 'Keith', 'Edwin', 'Kathryn', 'Douglas', 'Frances', 'Harvey', 'Carl', 'Dan', 'June', 'Karen', 'Elsie', 'Ron', 'Stanley', 'Nicholas', 'Danielle', 'Jose', 'Leesa', 'Audrea', 'Herbert', 'Melanie', 'Tonya', 'Jamie', 'Stacy', 'Oliver', 'Evelyn', 'Felix', 'Wilma', 'Oscar', 'Bruno', 'Linda', 'Mindy', 'Ashley', 'Nancy', 'Randolph', 'Jennifer', 'Janet', 'Guadalupe', 'Kimberly', 'Joan', 'Verna', 'Sarah', 'Clint', 'Jack', 'Billie', 'Daryl', 'Paul', 'Judy', 'Annette', 'Elizabeth', 'Justin', 'Donald', 'Ralph', 'Gene', 'Joel', 'Stephanie', 'Terri', 'Israel', 'Eleanor', 'Freida', 'Myrtle', 'Virginia', 'Roberta', 'Rhonda', 'Denny', 'Harley', 'Arthur', 'Laquita', 'Traci', 'Carolyn', 'Janee', 'Bruce', 'Steve', 'Norman', 'Rose', 'Kraig', 'Julie', 'Nicole', 'Esther', 'Edna', 'Lawrence', 'Bonnie', 'Maggie', 'Gerald', 'Lucia', 'Maureen', 'Susanna', 'Martin', 'Jay', 'Jorge', 'Reginald', 'Debra', 'Julius', 'Lester', 'Wallace', 'Cecil', 'Jared', 'Betty', 'Shaun', 'Crystal', 'Warren', 'Katherine', 'Freddy', 'Brian', 'Denise', 'Daniel', 'Susie', 'Helen', 'Lorna', 'Pearl', 'Jessie', 'Myra', 'Jessica', 'Beverly', 'Naomi', 'Winnie', 'Dolores', 'Reatha', 'Joshua', 'Christopher', 'Melissa', 'Elijah', 'Gabriel', 'Marsha', 'Eva', 'Fred', 'Phillip', 'Percy', 'Susan', 'Ricardo', 'Tracy', 'Amelia', 'Emily', 'Sandra', 'Kecia', 'Justina', 'Marvin', 'Constance', 'Andy', 'Stella', 'Ray', 'Iris', 'Deedee', 'Anita', 'Katina', 'Allan', 'Angelo', 'Cynthia', 'Shirley', 'Bryan', 'Patrick', 'Lewis', 'Russell', 'Christina', 'Sylvester', 'Wilbert', 'Joe', 'Roy', 'Wendy', 'Magdalena', 'Rudy', 'Valorie', 'Jamal', 'Glenda', 'Hortencia', 'Bernice', 'Todd', 'Walter', 'Tina', 'Rosella', 'Christy', 'Rosetta', 'Sally', 'Vannessa', 'Eric', 'Terry', 'Leroy', 'Isabel', 'Leonel', 'Jeffery', 'Pansy', 'George', 'Jacqueline', 'Anne', 'Estelle', 'Jeremy', 'Jesenia', 'Irene', 'Alice', 'Bernadette', 'Jana', 'Alton', 'Gregory', 'Erik', 'Al', 'Deangelo', 'Cheryl', 'Sophia', 'Heidi', 'Ervin', 'Andrew', 'Clyde', 'Angela', 'Cathy', 'Lane', 'Samuel', 'Vincenzo', 'Catherine', 'Antonia', 'Otis', 'Rachel', 'Alexander', 'Jacob', 'Philip', 'Dana', 'Fidela', 'Sonia', 'Louis', 'Dustin', 'Olivia', 'Bettie', 'Camille', 'Francis', 'Lauren', 'Kory', 'Letha', 'Steven', 'Glen', 'Ira', 'Sharon', 'Ella', 'Sue', 'Leonard', 'Kit', 'Theresa', 'Brenda', 'Casey', 'Spencer', 'Eloise', 'Anna', 'Minnie', 'Newton', 'Clarence', 'Henrietta', 'Anthony', 'Frank', 'Laura', 'Ronnie', 'Roberto', 'Dean', 'Dennis', 'Latonya', 'Jane', 'Fay', 'Bessie', 'Amber', 'Manda', 'Andrea', 'Willie', 'Julia', 'Antoinette', 'Erika', 'Kathleen', 'Claire', 'Debbie', 'Bennie', 'Kristi', 'Ryan', 'Christi', 'Veronica', 'Joyce', 'Jerry', 'Leta', 'Elbert', 'Lacy', 'Pamela', 'Humberto', 'Megan', 'Josh', 'Alexandra', 'Marie', 'Donita', 'Kenneth', 'Orlando', 'Mike', 'Lucille', 'Hubert', 'Micheal', 'Pete', 'Helene', 'India', 'Jeanette', 'Cecilia', 'Frederick', 'Darrel', 'Lavona', 'Janice', 'Cyrus', 'Felicia', 'Ruthie', 'Maryann', 'Randall', 'Lynn', 'Miguel', 'Ethel', 'Olga', 'Sean', 'Madge', 'Stephan', 'Amy', 'Brandy', 'Martha', 'Otto', 'Lucile', 'Chester', 'Elaine', 'Damian', 'Petra', 'Leslie', 'Carole', 'Billy', 'Willy', 'Joanne', 'Alison', 'Rosa', 'Charlie', 'Edward', 'Chris', 'Cassandra', 'Bradford', 'Ada', 'Shelly', 'Yvonne', 'Jean', 'Sid', 'Jasmine', 'Vita', 'Paulina', 'Daisy', 'Calvin', 'Temple', 'Carlos', 'Ruth', 'Marc', 'Grover', 'Christian', 'Valerie', 'Detra', 'Doris', 'Sylvia', 'Mona', 'Javier', 'Christine', 'Jacquelyn', 'Corey', 'Whitney', 'Afton', 'Jackson', 'Ellen', 'Hattie', 'Trina', 'Marilyn', 'Delores', 'Boyd', 'Shane', 'Jimmy', 'Ernest', 'Eddie', 'Lorinda', 'Everett', 'Rudolph', 'Logan', 'Fredrick', 'Adam', 'Josephine', 'Vernon', 'Lacie', 'Andre', 'Graham', 'Kristina', 'Angella', 'Curtis', 'Etta', 'Kathy', 'Nina', 'Elena', 'Travis', 'Maurice', 'Juana', 'Jim', 'Ian', 'Oma', 'Teri', 'Rosie', 'Jesse', 'Lorraine', 'Gloria', 'Fernando', 'Bridgette', 'Latasha', 'Lavern', 'Nadine', 'Cary', 'Dawn', 'Erica', 'Mildred', 'Matt', 'Henry', 'Ernestine', 'Melvin', 'Cole', 'Blanca', 'Claude', 'Benny', 'Elida', 'Theodore', 'Lamar', 'Gladys', 'Alvin', 'Darryl', 'Charlotte', 'Amanda', 'Thanh', 'Connie', 'Lindsay', 'Tish', 'Lorena', 'Laurie', 'Vince', 'Shannon', 'Tommy', 'Juan', 'Carmen', 'Ben', 'Angelina', 'Trenton', 'Marcella', 'Alyssa', 'Carmon', 'Lillie', 'Nichole', 'Tasha', 'Sonja', 'Cindy', 'Carol', 'Tamara', 'Lizzie', 'Bertha', 'Shu', 'Seth', 'Dwayne', 'Laurence', 'Rick', 'Geraldine', 'Zona', 'Virgil', 'Albert', 'Gus', 'Amparo', 'Lydia', 'Audrey', 'Juli', 'Winifred', 'Kim', 'Susana', 'Allen', 'Lucas', 'Ana', 'Tom', 'Lani', 'Rodolfo', 'Vickie', 'Margery', 'Miriam', 'Samantha', 'Don', 'Tobi', 'Alan', 'Verdie', 'Beth', 'Jeff', 'Callie', 'Chad', 'Paula', 'Natasha', 'Denice', 'Nicolle', 'Sheryl', 'Savanna', 'Ramiro', 'Ken', 'Nikki', 'Johnathan', 'Brandon', 'Kimberlee', 'Maryln', 'Alex', 'Aurelia', 'Josiah', 'Pat', 'Julianne', 'Alejandro', 'Claudie', 'Opal', 'Isreal', 'Kayla', 'Wm', 'Esperanza', 'Geneva', 'Allison', 'Louella', 'Mathew', 'Leilani', 'Aaron', 'Marva', 'Lynne', 'Earl', 'Myles', 'Rita', 'Kari', 'Johnny', 'Carla', 'Vicki', 'Peter', 'Stefanie', 'Wayne', 'Peggy', 'Simon', 'Barb', 'Romeo', 'Nathan', 'Mitchell', 'Ferdinand', 'Carson', 'Edith', 'Jackie', 'Scotty', 'Leif', 'Lela', 'Tena', 'Rebecca', 'Lee', 'Irish', 'Guy', 'Margie', 'Joesph', 'Claudette', 'Candelaria', 'Howard', 'Cori', 'April', 'Chelsea', 'Kyle', 'Kristin', 'Tyler', 'Donnie', 'Tara', 'Jill', 'Eli', 'Jan', 'Sidney', 'Micah', 'Jesus', 'Marjorie', 'Kimi', 'Johnathon', 'Tomi', 'Maura', 'Karina', 'Leo', 'Manual', 'Griselda', 'Jefferey', 'Lucy', 'Gerardo', 'Hilario', 'Tessie', 'Michele', 'Jenae', 'Albertine', 'Teofila', 'Terrance', 'Alfredo', 'Emmanuel', 'Ramon', 'Clarice', 'Fannie', 'Yong', 'Robyn', 'Johnnie', 'Agatha', 'Johanna', 'Darrin', 'Stacey', 'Tiffany', 'Willena', 'Emil', 'Misty', 'Bernita', 'Mee', 'Dominique', 'Shira', 'Molly', 'Moises', 'Shamika', 'Wendi', 'Rena', 'Wilmer', 'Orville', 'Latrice', 'Louise', 'Devin', 'Eileen', 'Liza', 'Consuelo', 'Lois', 'Pauline', 'Elva', 'Kelvin', 'Aida', 'Becky', 'Joey', 'Mozelle', 'Clifford', 'Zelma', 'Suzan', 'Kristopher', 'Shawn', 'Yesenia', 'Carroll', 'Kristen', 'Shaquana', 'Elisa', 'Wesley', 'Leona', 'Sara', 'Janine', 'Angeline', 'Loyd', 'Beau', 'Diego', 'Edythe', 'Edmond', 'Delia', 'Tana', 'Marcelina', 'Bob', 'Lynnette', 'Blanche', 'Williams', 'Melinda', 'Rosalyn', 'Margo', 'Salvador', 'Diana', 'Beatrice', 'Conrad', 'Renee', 'Thuy', 'Royal', 'Tim', 'Freddie', 'Deena', 'Judith', 'Novella', 'Yvette', 'Janina', 'Kenya', 'Dessie', 'Carmella', 'Clayton', 'Elmer', 'Francisco', 'Joy', 'Morris', 'Julian', 'Christoper', 'Vera', 'Victoria', 'Shawanda', 'Cody', 'Dewayne', 'Nelly', 'Leisa', 'Colton', 'Randell', 'Deirdre', 'Manuel', 'Muriel', 'Vivian', 'Son', 'Glenn', 'Zachary', 'Merle', 'Delora', 'Thurman', 'Sheila', 'Arnold', 'Quinton', 'Willard', 'Ava', 'Marguerite', 'Jeri', 'Andres', 'Johnie', 'Noe', 'Nathaniel', 'Felicita', 'Tanisha', 'Stanford', 'Marlene', 'Marcia', 'Blake', 'Marcus', 'Emma', 'Waldo', 'Rodney', 'Aldo', 'Imelda', 'Darrell', 'Yetta', 'Marcy', 'Tony', 'Hazel', 'Earlene', 'Gwen', 'Marianne', 'Jaime', 'Claudia', 'Cristal', 'Starla', 'Emilio', 'Saul', 'Barry', 'Jordan', 'Mariela', 'Dwight', 'Lanie', 'Lura', 'Marco', 'Malinda', 'Francisca', 'Gabrielle', 'Karl', 'Clifton', 'Shanita', 'Sheri', 'Jami', 'Marcos', 'Stewart', 'Nathanial', 'Ina', 'Leon', 'Neil', 'Alma', 'Delta', 'Regina', 'Rafael', 'Danny', 'Jeremiah', 'Gretchen', 'Grace', 'Irina', 'Vernie', 'Bill', 'Perry', 'Nellie', 'Tamika', 'Arlene', 'Franklin', 'Brett', 'Lawerence', 'Mabel', 'Sam', 'Garry', 'Eula', 'Jimmie', 'Leticia', 'Mason', 'Quentin', 'Jamaal', 'Violette', 'Edelmira', 'Margot', 'Cedric', 'Ezra', 'Tyrone', 'Zola', 'Hector', 'Ricky', 'Latoya', 'Bobbie', 'Reba', 'Paulette', 'Marge', 'Gordon', 'Larissa', 'Kelsey', 'Miles', 'Clinton', 'Kelley', 'Ollie', 'Brooke', 'Felisa', 'Craig', 'Karol', 'Dora', 'Austin', 'Nettie', 'Maxine', 'Vito', 'Oralee', 'Caitlin', 'Marta', 'Penny', 'Byron', 'Janis', 'Ruben', 'Anneliese', 'Arturo', 'Evie', 'Raquel', 'Lena', 'Doug', 'Stefani', 'Brittanie', 'Natalie', 'Omar', 'Sherry', 'Lonnie', 'Gail', 'Benedict', 'Kylie', 'Leeanne', 'Catalina', 'Christin', 'Claudio', 'Mervin', 'Gwendolyn', 'Lloyd', 'Geoffrey', 'Victor', 'Darlene', 'Dale', 'France', 'Thelma', 'Inez', 'Troy', 'Estrella', 'Anton', 'Eugenie', 'Harriett', 'Herman', 'Rogelio', 'Jeanne', 'Gertrude', 'Marlon', 'Rex', 'Kay', 'Archie', 'Melody', 'Abdul', 'Marla', 'Felton', 'Lavon', 'Zofia', 'Weldon', 'Desirae', 'Cesar', 'Damaris', 'Amie', 'Graciela', 'Reed', 'Christen', 'Zina', 'Ivan', 'Vincent', 'Vanessa', 'Floyd', 'Brendan', 'Kacey', 'Goldie', 'Merlin', 'Wiley', 'Jacklyn', 'Monique', 'Morgan', 'Flora', 'Renae', 'Leola', 'Adrian', 'Mable', 'Hugo', 'Jacelyn', 'Kara', 'Nilda', 'Eunice', 'Dante', 'Alberto', 'Ebony', 'Marisela', 'Lillian', 'Nolan', 'Coy', 'Alphonse', 'Nikita', 'Gina', 'Viola', 'Melba', 'Janette', 'Robin', 'Desmond', 'Rubi', 'Derek']

test_names = ['Thomas', 'Loretta', 'Harold', 'Courtney', 'Heather', 'Gary', 'Larry', 'Jonathan', 'Mark', 'Deborah', 'John', 'Stephen', 'David', 'Benjamin', 'Nicki', 'Joseph', 'Lori', 'Charles', 'Velma', 'Matthew', 'Bobby', 'Tammy', 'Raymond', 'Carrie', 'Maria', 'Tanya', 'Mary', 'Frankie', 'Sabrina', 'Ruby', 'Robert', 'Teresa', 'Dorothy', 'Patricia', 'Donna', 'Brandi', 'Scott', 'Jo', 'Antonio', 'Raphael', 'Damon', 'Richard', 'Norma', 'Timothy', 'Erin', 'Michelle', 'Kelly', 'Marion', 'Wilfredo', 'James']

test_not_name = ['Jody', 'Colleen', 'Greg', 'Tomas', 'Chelsie', 'Jon', 'Agnes', 'Harriet', 'Sherrie', 'Carolina', 'Annie', 'Lauretta', 'Leota', 'Darron', 'Kristine', 'Jenette', 'Rueben', 'Emiko', 'Harry', 'Phyllis', 'Hanna', 'Phyllis', 'Keisha', 'Kerry', 'Neal', 'Rosario', 'Ida', 'Mario', 'Harry', 'Foster', 'Roderick', 'Emerita', 'Sybil', 'Florence', 'Katie', 'Melida', 'Harris', 'Mario', 'Yolanda', 'Dave', 'Julio', 'Forrest', 'Maryanne', 'Chang', 'Dennise', 'Samual', 'Zane', 'Cora', 'Ida', 'Pedro'] #names not in dataset 

import names, random

# mock_data = []
# for i in range(1000): 
#     temp = names.get_first_name()
#     while temp in mock_data: 
#         temp = names.get_first_name()
#     mock_data.append(temp)        

test_names = []
for i in range(50): 
    temp = random.randint(0, 50)
    while mock_data[temp] in test_names:
        temp = random.randint(0, 50)
    test_names.append(mock_data[temp])

# test_not_name = [] 
# for i in range(50): 
#     temp = names.get_first_name()
#     while temp in mock_data: 
#         temp = names.get_first_name()
#     test_not_name.append(temp)

# print(mock_data)
# print("\n")
# print(test_names)
# print("\n")
# print(test_not_name)
# print("\n")

    