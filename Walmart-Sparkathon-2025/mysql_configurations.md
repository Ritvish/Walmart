# Common phpMyAdmin/MySQL configurations for BuddyCart

## Default XAMPP Configuration

DATABASE_URL=mysql+mysqlconnector://root:@localhost:3306/buddycart

## WAMP Configuration (if you set a password)

DATABASE_URL=mysql+mysqlconnector://root:your_password@localhost:3306/buddycart

## MAMP Configuration (default ports)

DATABASE_URL=mysql+mysqlconnector://root:root@localhost:8889/buddycart

## Custom MySQL Configuration

DATABASE_URL=mysql+mysqlconnector://your_username:your_password@localhost:3306/buddycart

## If you're using MySQL Workbench alongside phpMyAdmin

DATABASE_URL=mysql+mysqlconnector://root:your_mysql_password@localhost:3306/buddycart
