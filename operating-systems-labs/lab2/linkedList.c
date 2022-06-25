// A complete working C program to demonstrate all insertion methods
#include <stdio.h>
#include <stdlib.h>

// A linked list node
struct Node
{
    int data;
    int size;
    struct Node *next;
    struct Node *prev;
};


/* Given a reference (pointer to pointer) to the head of a list
   and an int, inserts a new node on the front of the list. */
void push(struct Node** head_ref, int new_data, int new_size){
    /* 1. allocate node */
    struct Node* new_node = (struct Node*) malloc(sizeof(struct Node));

    /* 2. put in the data  */
    new_node->data  = new_data;
    new_node->size  = new_size;

    /* 3. Make next of new node as head and previous as NULL */
    new_node->next = (*head_ref);
    new_node->prev = NULL;

    /* 4. change prev of head node to new node */
    if((*head_ref) !=  NULL)
      (*head_ref)->prev = new_node ;

    /* 5. move the head to point to the new node */
    (*head_ref)    = new_node;
}

/* Given a node as prev_node, insert a new node after the given node */
void insertAfter(struct Node *prev_node, int new_data, int new_size){
    /*1. check if the given prev_node is NULL */
    if (prev_node == NULL)
    {
        printf("the given previous node cannot be NULL");
        exit(0);
    }

    /* 2. allocate new node */
    struct Node* new_node =(struct Node*) malloc(sizeof(struct Node));

    /* 3. put in the data  */
    new_node->data  = new_data;
    new_node->size  = new_size;

    /* 4. Make next of new node as next of prev_node */
    new_node->next = prev_node->next;

    /* 5. Make the next of prev_node as new_node */
    prev_node->next = new_node;

    /* 6. Make prev_node as previous of new_node */
    new_node->prev = prev_node;

    /* 7. Change previous of new_node's next node */
    if (new_node->next != NULL)
      new_node->next->prev = new_node;
}

/* Given a reference (pointer to pointer) to the head
   of a DLL and an int, appends a new node at the end  */
void append(struct Node** head_ref, int new_data, int new_size){
    /* 1. allocate node */
    struct Node* new_node = (struct Node*) malloc(sizeof(struct Node));

    struct Node *last = *head_ref;  /* used in step 5*/

    /* 2. put in the data  */
    new_node->data  = new_data;
    new_node->size  = new_size;

    /* 3. This new node is going to be the last node, so
          make next of it as NULL*/
    new_node->next = NULL;

    /* 4. If the Linked List is empty, then make the new
          node as head */
    if (*head_ref == NULL)
    {
        new_node->prev = NULL;
        *head_ref = new_node;
        return;
    }

    /* 5. Else traverse till the last node */
    while (last->next != NULL)
        last = last->next;

    /* 6. Change the next of last node */
    last->next = new_node;

    /* 7. Make last node as previous of new node */
    new_node->prev = last;

    return;
}


int bestFit(struct Node *node, int new_data, int new_size){
  struct Node *iteratedNode = node;
  int currentWorstFit = -1;
  int j = 0;
  int currentWorstFitID = 0;
  if(node == NULL){
    return -1;
  }
  while(iteratedNode != NULL){    //first find the correct spot to put in new process
    if(iteratedNode->data == -1 && iteratedNode->size >= new_size //if the node is empty and the size is greater than or equal to the new process
      && (iteratedNode->size < currentWorstFit || currentWorstFit < 0))  {          //and if its better than the current best fit
        currentWorstFit = iteratedNode->size;
        currentWorstFitID = j;
    }
    iteratedNode = iteratedNode->next;
    j++;
  }
  int i = 0;
  if(currentWorstFit == -1){   //no spots
    return -1;
  }
  else{
    while(node != NULL){
      if(i == currentWorstFitID){
        if(node->size == new_size){ //if the current block is the size of the new block do nothing special
          node->size = new_size;
          node->data = new_data;
          return 0;
        }
        else{   //split block by inserting new node and make its data -1 and size = oldsize - new_size
          insertAfter(node, new_data, new_size);
          node->size = (node->size - new_size);
          return 0;
        }
      }
      node = node->next;
      i++;
    }
  }
  return 0;
}

int worstFit(struct Node *node, int new_data, int new_size){
  struct Node *iteratedNode = node;
  int currentWorstFit = 0;
  int j = 0;
  int currentWorstFitID = 0;
  if(node == NULL){
    return -1;
  }
  while(iteratedNode != NULL){    //first find the correct spot to put in new process
    if(iteratedNode->data == -1 && iteratedNode->size >= new_size //if the node is empty and the size is greater than or equal to the new process
      && iteratedNode->size > currentWorstFit)  {          //and if its better than the current best fit
        currentWorstFit = iteratedNode->size;
        currentWorstFitID = j;
    }
    iteratedNode = iteratedNode->next;
    j++;
  }
  int i = 0;
  if(currentWorstFit == -1){   //no spots
    return -1;
  }
  else{
    while(node != NULL){
      if(i == currentWorstFitID){
        if(node->size == new_size){ //if the current block is the size of the new block do nothing special
          node->size = new_size;
          node->data = new_data;
          return 0;
        }
        else{   //split block by inserting new node and make its data -1 and size = oldsize - new_size
          insertAfter(node, new_data, new_size);
          node->size = (node->size - new_size);
          return 0;
        }
      }
      node = node->next;
      i++;
    }
  }
  return 0;
}

/* Removes Process from the list. Sets data to -1 to show that its block is
   is now empty and ready to be used again */
void takeProcessOff(struct Node *node, int identifier){
  while (node != NULL){
    if(node-> data == identifier){
      node->data = -1;
      break;
    }
    node = node->next;
  }
}

// Removes node completely from list
void removeNode(struct Node *node, int identifier){
  while (node != NULL)
  {
      if(node->data == identifier)
      {
        printf("%s\n", "LOCATED NODE TO BE REMOVED");
        struct Node* nextNode =  node->next;
        node = node->prev;
        node->next = nextNode;
        break;
      }
      node = node->next;
  }
} //not used!

// If there are insances where there are multiple empty blocks in a row
void cleanUpList(struct Node *node){
  while (node != NULL && node->next != NULL){
    if(node->data == -1 && node->next->data == -1){
        node->size += node->next->size;
        node->next = node->next->next;
    }
    node = node->next;
  }
  //TODO move other cleanup in here
}

void removeProcess(struct Node *node, int identifier){
  takeProcessOff(node, identifier);  //remove 4. so linked list becomes 1->7->8->6->(-1)->NULL
  cleanUpList(node);
  /*if(node->data == -1){   //if the top of the list is empty remove it to clean up space
    node = node->next;    //this is supposed to be in cleanUpList but its not working...
    node->prev = NULL;
  }*/
}

// This function prints contents of linked list starting from the given node
void printList(struct Node *node){
    //struct Node *last;
    printf("Created DLL is: ");
    printf("Traversal in forward direction \n");
    while (node != NULL)
    {
        printf("Data: %d Size: %d \n", node->data, node->size);
        //last = node;
        node = node->next;
    }
    /*printf("\nTraversal in reverse direction \n");
    while (last != NULL)
    {
        printf("Data: %d Size: %d \n", last->data, last->size);
        last = last->prev;
    }*/
}

/* Driver program to test above functions*/
int main()
{
    /* Start with the empty list */
    struct Node* head = NULL;

    push(&head, -1, 10);
    // Insert 6.  So linked list becomes 6->NULL
    if(bestFit(head, 6, 10) == -1)
      push(&head, 6, 10);
    // Insert 7 at the beginning. So linked list becomes 7->6->NULL
    push(&head, 7, 10);

    // Insert 1 at the beginning. So linked list becomes 1->7->6->NULL
    push(&head, 1, 15);

    // Insert 4 at the end. So linked list becomes 1->7->6->4->NULL
    append(&head, 4, 20);

    // Insert 8, after 7. So linked list becomes 1->7->8->6->4->NULL
    insertAfter(head->next, 8, 9);


    printList(head);

    //Tests Removal functions

    removeProcess(head, 4);  //Removes Process 4   1->7->8->6->(-1)->NULL
    printList(head);
    removeProcess(head, 6);  //Removes Process 1   1->7->8->(-1)->NULL  should be 7->8->6->(-1)->NULL
    printList(head);
    removeProcess(head, 8);  //Removes Process 7   1->(-1)->NULL        should be 8->6->(-1)->NULL
    if(head->data == -1){   //if the top of the list is empty remove it to clean up space, needs to be called after a remove
      head = head->next;    //this is supposed to be in cleanUpList but its not working...
      head->prev = NULL;
    }
    printList(head);

    //Tests Best Fit
    printList(head);
    if(bestFit(head, 10, 10) == -1)
      push(&head, 10, 10);  //Add in 10 so linked list becomes 8->6->(-1)->10->NULL
    push(&head, -1, 100);
    printList(head);
    if(worstFit(head, 22, 10) == -1)
      push(&head, 22, 10);
    printList(head);


    //getchar();

    return 0;
}
