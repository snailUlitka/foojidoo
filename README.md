# fooJIdoo

A food delivery service where restaurants publish menus with dishes. Users browse the menu, create orders, choose payment and delivery methods.

## Database Scheme (Tables)

### User
- user\_id (PK)
- name
- phone
- address
- password

### Restaurant

- restaurant\_id (PK)
- name
- description
- address
- phone

### Dish

- dish\_id (PK)
- restaurant\_id (PK) (FK -> Restaurant.id)
- name
- description
- price

### Order (Cart)

- user\_id (PK) (FK -> User.id)
- status (e.g., pending, preparing, delivering, delivered, cancelled)
- payment\_method (e.g., card, cash, online)
- created\_at

### OrderItem

- dish\_id (PK) (FK -> Dish.id)
- user\_id (PK) (FK -> User.id)
- restaurant\_id (PK) (FK -> Restaurant.id)
- quantity
