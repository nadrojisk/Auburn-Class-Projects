
/*****************************************************************************\
* Laboratory Exercises COMP 3500                                              *
* Author: Saad Biaz                                                           *
* Updated 6/5/2017 to distribute to students to redo Lab 1                    *
* Updated 5/9/2017 for COMP 3500 labs                                         *
* Date  : February 20, 2009                                                   *
\*****************************************************************************/

/*****************************************************************************\
*                             Global system headers                           *
\*****************************************************************************/


#include "common2.h"

/*****************************************************************************\
*                             Global data types                               *
\*****************************************************************************/

typedef enum {TAT,RT,CBT,THGT,WT, JQ} Metric;


/*****************************************************************************\
*                             Global definitions                              *
\*****************************************************************************/
#define MAX_QUEUE_SIZE 10
#define FCFS            1
#define RR              3

#define OMAP            0
#define PAGING          1
#define BESTFIT         2
#define WORSTFIT        3
#define NONE            -1

#define PAGESIZE        256

#define MAXMETRICS      6



/*****************************************************************************\
*                            Global data structures                           *
\*****************************************************************************/




/*****************************************************************************\
*                                  Global data                                *
\*****************************************************************************/

Quantity NumberofJobs[MAXMETRICS]; // Number of Jobs for which metric was collected
Average  SumMetrics[MAXMETRICS]; // Sum for each Metrics
int memoryPolicy = WORSTFIT;

int  pagesAvailable = 1048576 / PAGESIZE;
int  nonavailabalePages = 0;
struct Node* head = NULL;
//int pages_size = *(&Pages + 1) - Pages;
//int pagesAvailable;

/*****************************************************************************\
*                               Function prototypes                           *
\*****************************************************************************/

void                 ManageProcesses(void);
void                 NewJobIn(ProcessControlBlock whichProcess);
void                 BookKeeping(void);
Flag                 ManagementInitialization(void);
void                 LongtermScheduler(void);
void                 IO();
void                 CPUScheduler(Identifier whichPolicy);
ProcessControlBlock *SRTF();
void                 Dispatcher();
void                 checkForMissingPages();

// A linked list node
struct Node{
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
void insertAfter(struct Node* prev_node, int new_data, int new_size){
    /*1. check if the given prev_node is NULL */
    if (prev_node == NULL)
    {
        printf("the given previous node cannot be NULL\n");
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
  int currentBestFit = -1;
  int j = 0;
  int currentBestFitID = 0;
  if(node == NULL){
    return -1;
  }
  while(iteratedNode != NULL){    //first find the correct spot to put in new process
    if(iteratedNode->data == -1 && iteratedNode->size >= new_size //if the node is empty and the size is greater than or equal to the new process
      && (iteratedNode->size < currentBestFit || currentBestFit < 0))  {          //and if its better than the current best fit
        currentBestFit = iteratedNode->size;
        currentBestFitID = j;
    }
    iteratedNode = iteratedNode->next;
    j++;
  }
  int i = 0;
  if(currentBestFit == -1){   //no spots
    return -1;
  }
  else{
    while(node != NULL){
      if(i == currentBestFitID){
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
    printf("%s\n", "List:");
    while (node != NULL)
    {
        printf("Data: %d Size: %d \n", node->data, node->size);
        //last = node;
        node = node->next;
    }
    printf("\n" );
    /*printf("\nTraversal in reverse direction \n");
    while (last != NULL)
    {
        printf("Data: %d Size: %d \n", last->data, last->size);
        last = last->prev;
    }*/
}


/*****************************************************************************\
* function: main()                                                            *
* usage:    Create an artificial environment operating systems. The parent    *
*           process is the "Operating Systems" managing the processes using   *
*           the resources (CPU and Memory) of the system                      *
*******************************************************************************
* Inputs: ANSI flat C command line parameters                                 *
* Output: None                                                                *
*                                                                             *
* INITIALIZE PROGRAM ENVIRONMENT                                              *
* START CONTROL ROUTINE                                                       *
\*****************************************************************************/

int main (int argc, char **argv) {
   if (Initialization(argc,argv)){
     ManageProcesses();
   }
} /* end of main function */

/***********************************************************************\
* Input : none                                                          *
* Output: None                                                          *
* Function: Monitor Sources and process events (written by students)    *
\***********************************************************************/

void ManageProcesses(void){
  ManagementInitialization();
  while (1) {
    IO();
    CPUScheduler(PolicyNumber);
    Dispatcher();

  }
}

/***********************************************************************\
* Input : none                                                          *
* Output: None                                                          *
* Function:                                                             *
*    1) if CPU Burst done, then move process on CPU to Waiting Queue    *
*         otherwise (RR) return to rReady Queue                         *
*    2) scan Waiting Queue to find processes with complete I/O          *
*           and move them to Ready Queue                                *
\***********************************************************************/
void IO() {
  ProcessControlBlock *currentProcess = DequeueProcess(RUNNINGQUEUE);
  if (currentProcess){
    if (currentProcess->RemainingCpuBurstTime <= 0) { // Finished current CPU Burst
      currentProcess->TimeEnterWaiting = Now(); // Record when entered the waiting queue
      EnqueueProcess(WAITINGQUEUE, currentProcess); // Move to Waiting Queue
      currentProcess->TimeIOBurstDone = Now() + currentProcess->IOBurstTime; // Record when IO completes
      currentProcess->state = WAITING;
    } else { // Must return to Ready Queue
      currentProcess->JobStartTime = Now();
      EnqueueProcess(READYQUEUE, currentProcess); // Mobe back to Ready Queue
      currentProcess->state = READY; // Update PCB state
    }
  }

  /* Scan Waiting Queue to find processes that got IOs  complete*/
  ProcessControlBlock *ProcessToMove;
  /* Scan Waiting List to find processes that got complete IOs */
  ProcessToMove = DequeueProcess(WAITINGQUEUE);
  if (ProcessToMove){
    Identifier IDFirstProcess =ProcessToMove->ProcessID;
    EnqueueProcess(WAITINGQUEUE,ProcessToMove);
    ProcessToMove = DequeueProcess(WAITINGQUEUE);
    while (ProcessToMove){
      if (Now()>=ProcessToMove->TimeIOBurstDone){
	ProcessToMove->RemainingCpuBurstTime = ProcessToMove->CpuBurstTime;
	ProcessToMove->JobStartTime = Now();
	EnqueueProcess(READYQUEUE,ProcessToMove);
      } else {
	EnqueueProcess(WAITINGQUEUE,ProcessToMove);
      }
      if (ProcessToMove->ProcessID == IDFirstProcess){
	break;
      }
      ProcessToMove =DequeueProcess(WAITINGQUEUE);
    } // while (ProcessToMove)
  } // if (ProcessToMove)
}

/***********************************************************************\
 * Input : whichPolicy (1:FCFS, 2: SRTF, and 3:RR)                      *
 * Output: None                                                         *
 * Function: Selects Process from Ready Queue and Puts it on Running Q. *
\***********************************************************************/
void CPUScheduler(Identifier whichPolicy) {
  ProcessControlBlock *selectedProcess;
  if ((whichPolicy == FCFS) || (whichPolicy == RR)) {
    selectedProcess = DequeueProcess(READYQUEUE);
  } else{ // Shortest Remaining Time First
    selectedProcess = SRTF();
  }
  if (selectedProcess) {
    selectedProcess->state = RUNNING; // Process state becomes Running
    EnqueueProcess(RUNNINGQUEUE, selectedProcess); // Put process in Running Queue
  }
}

/***********************************************************************\
 * Input : None                                                         *
 * Output: Pointer to the process with shortest remaining time (SRTF)   *
 * Function: Returns process control block with SRTF                    *
\***********************************************************************/
ProcessControlBlock *SRTF() {
  /* Select Process with Shortest Remaining Time*/
  ProcessControlBlock *selectedProcess, *currentProcess = DequeueProcess(READYQUEUE);
  selectedProcess = (ProcessControlBlock *) NULL;
  if (currentProcess){
    TimePeriod shortestRemainingTime = currentProcess->TotalJobDuration - currentProcess->TimeInCpu;
    Identifier IDFirstProcess =currentProcess->ProcessID;
    EnqueueProcess(READYQUEUE,currentProcess);
    currentProcess = DequeueProcess(READYQUEUE);
    while (currentProcess){
      if (shortestRemainingTime >= (currentProcess->TotalJobDuration - currentProcess->TimeInCpu)){
	EnqueueProcess(READYQUEUE,selectedProcess);
	selectedProcess = currentProcess;
	shortestRemainingTime = currentProcess->TotalJobDuration - currentProcess->TimeInCpu;
      } else {
	EnqueueProcess(READYQUEUE,currentProcess);
      }
      if (currentProcess->ProcessID == IDFirstProcess){
	break;
      }
      currentProcess =DequeueProcess(READYQUEUE);
    } // while (ProcessToMove)
  } // if (currentProcess)
  return(selectedProcess);
}

/***********************************************************************\
 * Input : None                                                         *
 * Output: None                                                         *
 * Function:                                                            *
 *  1)If process in Running Queue needs computation, put it on CPU      *
 *              else move process from running queue to Exit Queue      *
\***********************************************************************/
void Dispatcher() {
  double start;
  int pagesToBeReleased;
  ProcessControlBlock *processOnCPU = Queues[RUNNINGQUEUE].Tail; // Pick Process on CPU
  if (!processOnCPU) { // No Process in Running Queue, i.e., on CPU
    return;
  }
  if(processOnCPU->TimeInCpu == 0.0) { // First time this process gets the CPU
    SumMetrics[RT] += Now()- processOnCPU->JobArrivalTime;
    NumberofJobs[RT]++;
    processOnCPU->StartCpuTime = Now(); // Set StartCpuTime
  }
  if (processOnCPU->TimeInCpu >= processOnCPU-> TotalJobDuration) { // Process Complete
    if (memoryPolicy == OMAP){
        AvailableMemory += processOnCPU->MemoryRequested; //release memory being held by process
    }
    else if (memoryPolicy == PAGING){
        pagesToBeReleased = (processOnCPU->MemoryRequested / PAGESIZE); //Calculating the number of pages and rounds it up
        if(processOnCPU->MemoryRequested % PAGESIZE > 0){
          pagesToBeReleased++;
        }
        pagesAvailable += pagesToBeReleased;
        nonavailabalePages -= pagesToBeReleased;
        checkForMissingPages();
    }
    else if (memoryPolicy == BESTFIT || memoryPolicy == WORSTFIT){
      AvailableMemory += processOnCPU->MemoryRequested;
      removeProcess(head, processOnCPU->ProcessID);
    }

    NumberofJobs[THGT]++;
    NumberofJobs[TAT]++;
    NumberofJobs[WT]++;
    NumberofJobs[CBT]++;

    printf(" >>>>>Process # %d complete, %d Processes Completed So Far<<<<<<\n",
	  processOnCPU->ProcessID,NumberofJobs[THGT]);
    processOnCPU=DequeueProcess(RUNNINGQUEUE);
    EnqueueProcess(EXITQUEUE,processOnCPU);


    SumMetrics[TAT]     += Now() - processOnCPU->JobArrivalTime;
    SumMetrics[WT]      += processOnCPU->TimeInReadyQueue;


    // processOnCPU = DequeueProcess(EXITQUEUE);
    // XXX free(processOnCPU);

  }
  else { // Process still needs computing, out it on CPU
    TimePeriod CpuBurstTime = processOnCPU->CpuBurstTime;
    processOnCPU->TimeInReadyQueue += Now() - processOnCPU->JobStartTime;
    if (PolicyNumber == RR){
      CpuBurstTime = Quantum;
      if (processOnCPU->RemainingCpuBurstTime < Quantum)
	     CpuBurstTime = processOnCPU->RemainingCpuBurstTime;
    }
    processOnCPU->RemainingCpuBurstTime -= CpuBurstTime;
    // SB_ 6/4 End Fixes RR
    TimePeriod StartExecution = Now();
    OnCPU(processOnCPU, CpuBurstTime); // SB_ 6/4 use CpuBurstTime instead of PCB-> CpuBurstTime
    processOnCPU->TimeInCpu += CpuBurstTime; // SB_ 6/4 use CpuBurstTime instead of PCB-> CpuBurstTimeu
    SumMetrics[CBT] += CpuBurstTime;
  }
}

/***********************************************************************\
* Input : None                                                          *
* Output: None                                                          *
* Function: This routine is run when a job is added to the Job Queue    *
\***********************************************************************/
void NewJobIn(ProcessControlBlock whichProcess){
  ProcessControlBlock *NewProcess;
  /* Add Job to the Job Queue */
  NewProcess = (ProcessControlBlock *) malloc(sizeof(ProcessControlBlock));
  memcpy(NewProcess,&whichProcess,sizeof(whichProcess));
  NewProcess->TimeInCpu = 0; // Fixes TUX error
  NewProcess->RemainingCpuBurstTime = NewProcess->CpuBurstTime; // SB_ 6/4 Fixes RR
  EnqueueProcess(JOBQUEUE,NewProcess);
  DisplayQueue("Job Queue in NewJobIn",JOBQUEUE);
  LongtermScheduler(); /* Job Admission  */
}


/***********************************************************************\
* Input : None                                                         *
* Output: None                                                         *
* Function:                                                            *
* 1) BookKeeping is called automatically when 250 arrived              *
* 2) Computes and display metrics: average turnaround  time, throughput*
*     average response time, average waiting time in ready queue,      *
*     and CPU Utilization                                              *
\***********************************************************************/
void BookKeeping(void){
  double end = Now(); // Total time for all processes to arrive
  Metric m;

  // Compute averages and final results
  if (NumberofJobs[TAT] > 0){
    SumMetrics[TAT] = SumMetrics[TAT]/ (Average) NumberofJobs[TAT];
  }
  if (NumberofJobs[RT] > 0){
    SumMetrics[RT] = SumMetrics[RT]/ (Average) NumberofJobs[RT];
  }
  SumMetrics[CBT] = SumMetrics[CBT]/ Now();

  if (NumberofJobs[WT] > 0){
    SumMetrics[WT] = SumMetrics[WT]/ (Average) NumberofJobs[WT];
  }

  if (NumberofJobs[JQ] > 0){
    SumMetrics[JQ] = SumMetrics[JQ]/ (Average) NumberofJobs[JQ];
  }
  printf("\n********* Processes Managemenent Numbers ******************************\n");
  printf("Policy Number = %d, Quantum = %.6f   Show = %d\n", PolicyNumber, Quantum, Show);
  printf("Number of Completed Processes = %d\n", NumberofJobs[THGT]);
  printf("ATAT=%f   ART=%f  CBT = %f  T=%f AWT=%f  AWTJQ=%f\n\a",
	SumMetrics[TAT], SumMetrics[RT], SumMetrics[CBT],
	NumberofJobs[THGT]/Now(), SumMetrics[WT], SumMetrics[JQ]);
  exit(0);
}

/***********************************************************************\
* Input : None                                                          *
* Output: None                                                          *
* Function: Decides which processes should be admitted in Ready Queue   *
*           If enough memory and within multiprogramming limit,         *
*           then move Process from Job Queue to Ready Queue             *
\***********************************************************************/
void LongtermScheduler(void){
  ProcessControlBlock *currentProcess = DequeueProcess(JOBQUEUE);
  while (currentProcess) {
    if(memoryPolicy == OMAP){
        //if there is enough memory admit process
        if (AvailableMemory >= currentProcess->MemoryRequested){
          AvailableMemory -= currentProcess->MemoryRequested;
        }
        else{ //make sure to put process back on queue if not enough memory
          EnqueueProcess(JOBQUEUE, currentProcess);
          printf(" >>>>>Not enough Memory for Process to be Admitted<<<<<<\n");
          return;
        }
    }
    else if(memoryPolicy == PAGING){
        int pagesRequested = (currentProcess->MemoryRequested / PAGESIZE); //Calculating the number of pages
        if(currentProcess->MemoryRequested % PAGESIZE > 0){                    //rounds up pages if any remainder
          pagesRequested++;
        }
        printf("Pages Available: %d Pages Requested: %d Pages Taken: %d\n" , pagesAvailable, pagesRequested, nonavailabalePages);
        if(pagesRequested <= pagesAvailable){ //if there are enough pages left
          pagesAvailable -= pagesRequested;
          nonavailabalePages += pagesRequested;
          checkForMissingPages();  //checks to make sure pages have gone missing. can be removed later
        }
        else{   //not enough pages left
          printf(">>>>>Number of requested pages exceeds the amount of available pages<<<<<<\n");
          EnqueueProcess(JOBQUEUE, currentProcess);
          return;
        }
      }
    else if(memoryPolicy == BESTFIT){
      if(AvailableMemory >= currentProcess->MemoryRequested){
          if(bestFit(head, currentProcess->ProcessID, currentProcess->MemoryRequested) == -1){
              push(&head, currentProcess->ProcessID, currentProcess->MemoryRequested);
            }
          if(head->data == -1){   //if the top of the list is empty remove it to clean up space, needs to be called after a remove
            head = head->next;    //this is supposed to be in cleanUpList but its not working...
            head->prev = NULL;
          }
          //printList(head);
          AvailableMemory-= currentProcess->MemoryRequested;
      }
      else{ //not enough space
        printf(">>>>>Number of requested pages exceeds the amount of available memory<<<<<<\n");
        EnqueueProcess(JOBQUEUE, currentProcess);
        return;
      }
    }
    else if(memoryPolicy == WORSTFIT){
      if(AvailableMemory >= currentProcess->MemoryRequested){
          if(worstFit(head, currentProcess->ProcessID, currentProcess->MemoryRequested) == -1){
              push(&head, currentProcess->ProcessID, currentProcess->MemoryRequested);
            }
          if(head->data == -1){   //if the top of the list is empty remove it to clean up space, needs to be called after a remove
            head = head->next;    //this is supposed to be in cleanUpList but its not working...
            head->prev = NULL;
          }
          //printList(head);
          AvailableMemory-= currentProcess->MemoryRequested;
      }
      else{ //not enough space
        printf(">>>>>Number of requested pages exceeds the amount of available memory<<<<<<\n");
        EnqueueProcess(JOBQUEUE, currentProcess);
        return;
      }
    }
    currentProcess->TimeInJobQueue = Now() - currentProcess->JobArrivalTime; // Set TimeInJobQueue
    currentProcess->JobStartTime = Now(); // Set JobStartTime
    EnqueueProcess(READYQUEUE,currentProcess); // Place process in Ready Queue
    currentProcess->state = READY; // Update process state
    NumberofJobs[JQ]++;
    SumMetrics[JQ]      += currentProcess->TimeInJobQueue;
    currentProcess = DequeueProcess(JOBQUEUE);
  }
}


/***********************************************************************\
* Input : None                                                          *
* Output: TRUE if Intialization successful                              *
\***********************************************************************/
Flag ManagementInitialization(void){
  Metric m;
  for (m = TAT; m < MAXMETRICS; m++){
     NumberofJobs[m] = 0;
     SumMetrics[m]   = 0.0;
  }
  return TRUE;
}

void checkForMissingPages(){
  if(pagesAvailable + nonavailabalePages != (1048576 / PAGESIZE)){ //check to make sure we aren't loosing track of pages somehow
    printf(">>>>Error Pages have gotten lost somehow<<<<\nPages Available: %d Pages Taken: %d\n" , pagesAvailable, nonavailabalePages);
    exit(0);
  }
}
