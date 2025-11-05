"""Shopping list

add_item(item)
remove_item(item_id) -> true, false
get_item(item_id) -> dictionary
get_all_items() -> list

"""
import json
from typing import List



class  ShoppingList:
    """Makes a shopping list.

    Attributes:
        items(list): List of dictionaries containing shopping items.

    Examples:
        >>> shopping_list = ShoppingList()
        >>> shopping_list.add_items(items_name="Books", quantity=4)
        >>> shopping_list.get_items()
        [{'item_name': 'Books', 'quantity': 4}]
    """

    def __init__(self):
        """Initialize an empty shopping list.

        """
        self.items = []
    
    def add_item(self, item_name: str, quantity: int = 1)->None:
        """Add an item. 
        """
        self.items.append({
            "item_name" : item_name,
            "quantity" : quantity
        })
    
    def get_items(self)->List:
        """
        Returns a list of all items.

        Args:
            None
        
        Returns:
            List of items
        
        Example:
            >>> your_items = self.list_items()
        """
        all_items = self.items.copy()
        return all_items
    
    def remove_item(self, item_name: str) -> bool:
        for item in self.items:
            if item["item_name"] == item_name:
                self.items.remove(item)
                return True
        return False

    def get_item(self, item_name: str) -> dict:
        for item in self.items:
            if item["item_name"] == item_name:
                return item
        return {}

    
    def __str__(self) -> str:
        return f"All items ({len(self.items)}):\n" + "\n".join(
            f"- {item['item_name']} (x{item['quantity']})" for item in self.items
            )


my_shopping_list = ShoppingList()
my_shopping_list.add_item(item_name="Books", quantity=10)
my_shopping_list.add_item("Chips", quantity=3)
print(my_shopping_list)
        
from dataclasses import dataclass, field, asdict

@dataclass
class ShoppingItem:
    item_id: int
    item_name: str
    item_quantity: int

@dataclass
class NewShoppingList:
    shopping_list_id : int
    customer_name: str
    items: List[ShoppingItem] =  field(default_factory=list)

sl_items = [
    ShoppingItem(item_id=1, item_name="Phones", item_quantity=5),
    ShoppingItem(item_id=2, item_name="Tablet", item_quantity=5),
]
sl = NewShoppingList(shopping_list_id=1, customer_name="Ian", items=sl_items)

print(f"{sl}")

with open("shopping_list.json","w") as file:
    json.dump(asdict(sl), file, indent=4)

sl2 = NewShoppingList(shopping_list_id=2, customer_name="Brian", items=sl_items)
with open("shopping_list.json","a") as file:
    json.dump(asdict(sl2), file, indent=4)