# Operating Systems Labs
Labs for Dr. Biaz's COMP-3500 Introduction to Operating Systems Summer 2018 at Auburn University
### Lab 1: Emulating Three CPU Schedulers [Short-Term Scheduler]
1. [First Come First Serve (FCFS)](https://en.wikipedia.org/wiki/FIFO_(computing_and_electronics))
    * First Come First Serve is the simplest CPU Scheduler. It looks at the current jobs waiting to run as a stack and will take the first one in and run it and after it is done running it will grab the next process
    * FCFS has amazing throughput due to low context switching however its response time is very poor
2. [Shortest Job First (SJF)](https://en.wikipedia.org/wiki/Shortest_job_next)
    * Shortest Job First will look at the time that it will take for a job to complete and pick the smallest one
    * Its throughput is not as good as FCFS but not as bad as RR
    * Its response time however is much better than FCFS but not as good as RR
    * However it is unrealistic because most of the time the Operating System will not know how much time remaining a job will have.
3. [Round Robin (RR)](https://en.wikipedia.org/wiki/Round-robin_scheduling)
    * Round Robin makes up for SJF shortcomings by establishing a quantum, or time interval, at which the OS will premptively swap out a process
    * RR does not check to see how long a job has left, it simply grabs the first one in the queue and will run it for its quantum. If it still has time left it will go back on the queue, if not it will exit.
    * RR throughput is the worst out of the three due to its context switching but its response time is the highest
    
#### Compiling and Executing Lab 1
* To compile lab 1 type: cc -o pm processesgenerator.o processesmanagement.c -lm
  * "pm" will be the name of the file that is created by the compiler
* To run lab 1 type: ./pm [arg1] [arg2]
  * Where arg1 takes a value 1, 2, or 3 for FCFS, SJF, and RR
  * arg2, which is only used if arg1 is equal to 3, takes a value in milliseconds which is used to set the quantum.
### Lab 2: Emulating Five Medium-Term Schedulers and Long-Term Schedulers
1. "No Memory Policy"
    * Essentially this is just lab 1. This is a base line to compare with the policies that actually enforce memory.
2. Optimal Memory Allocation Policy (OMAP)
    * OMAP does not worry about where the memory is placed. It will simply check to see if there is enough memory for the new process and if there is it will subtract the memory request from the memory available. When the process is finished the memory is added back.
3. Paging Policy
    * Available Memory is expressed in terms of Number of Available Pages and as long as the Pages Requested is smaller or equal to that value new processes can be added.
    * Implemeted Page Sizes 256 Bytes and 8 KB (8129 Bytes)
4. [Best-Fit Policy](https://courses.cs.vt.edu/csonline/OS/Lessons/MemoryAllocation/index.html)
    * Best-Fit will check the current memory stack and find the "best-fit," the smallest "hole" that the new process can fit in. 
    * Searches from bottom to top.
    * Best-Fit and Worst-Fit also implement memory compaction. So if there are neighboring "holes" they will be merged together into one larger hole. Also if there is a hole ontop of the memory stack it will simply be removed since there is no reason for it to be there.
5. [Worst-Fit Policy](https://courses.cs.vt.edu/csonline/OS/Lessons/MemoryAllocation/index.html)
    * Worst-Fit is simpilar to Best-Fit in how it operates but instead of finding the smallest hole, it will find the largest one.

#### Compiling and Executing Lab 1
* Inside you will need to set memoryPolicy in the global data section to either NONE, OMAP, BESTFIT, or WORSTFIT
* After that save and exit then you can compile the program.
* To compile lab 1 type: cc -o pm processesgenerator.o processesmanagement.c -lm
  * "pm" will be the name of the file that is created by the compiler
* To run lab 1 type: ./pm [arg1] [arg2]
  * Where arg1 takes a value 1, 2, or 3 for FCFS, SJF, and RR
  * arg2, which is only used if arg1 is equal to 3, takes a value in milliseconds which is used to set the quantum.
