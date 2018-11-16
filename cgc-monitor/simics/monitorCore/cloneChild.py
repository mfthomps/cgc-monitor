from simics import *
'''
Run until the current process issues the clone system call and we start 
executing within the child.
'''
class CloneChild():
    def __init__(self, top, cell, param, mem_utils, task_utils, context_manager, lgr):
        self.lgr = lgr
        self.top = top
        self.mem_utils = mem_utils
        self.task_utils = task_utils
        self.param = param
        self.context_manager = context_manager
        self.cpu, self.comm, self.pid = self.task_utils.curProc() 
        callnum = task_utils.syscallNumber('clone')
        entry = self.task_utils.getSyscallEntry(callnum)
        self.lgr.debug('cloneChild callnum is %s entry 0x%x' % (callnum, entry))
        self.call_break = self.context_manager.genBreakpoint(cell, Sim_Break_Linear, Sim_Access_Execute, entry, 1, 0)
        self.call_hap = self.context_manager.genHapIndex("Core_Breakpoint_Memop", self.syscallHap, None, self.call_break)
        self.exit_break = None
        self.exit_hap = None
        self.child_pid = None

    def syscallHap(self, dumb, third, forth, memory):
        cpu = SIM_current_processor()
        if cpu != self.cpu:
            self.lgr.debug('cloneChild syscallHap, wrong cpu %s %s' % (cpu.name, self.cpu.name))
            return
        cpu, comm, pid = self.task_utils.curProc() 
        if self.pid != pid: 
            self.lgr.debug('cloneChild syscallHap looked for pid %d, found %d.  Do nothing' % (self.pid, pid))
            return

        self.context_manager.genDeleteHap(self.call_hap)        
        break_eip = self.top.getEIP()
        stack_frame = None
        stack_frame = self.task_utils.frameFromStackSyscall()

        phys = self.mem_utils.v2p(self.cpu, stack_frame['eip'])
        self.lgr.debug('cloneChild syscallHap set break at 0x%x (0x%x)' % (stack_frame['eip'], phys))
        self.exit_break = self.context_manager.genBreakpoint(self.cpu.physical_memory, Sim_Break_Physical, Sim_Access_Execute, phys, 1, 0)
        self.exit_hap = self.context_manager.genHapIndex("Core_Breakpoint_Memop", self.exitHap, cpu, self.exit_break)


    def exitHap(self, dumb, third, forth, memory):
        if self.exitHap is None:
            return
        cpu, comm, pid = self.task_utils.curProc() 
        if self.cpu != cpu:
                return
        if self.pid == pid:
            ''' returned from parent '''
            reg_num = self.cpu.iface.int_register.get_number('eax')
            ueax = self.cpu.iface.int_register.read(reg_num)
            eax = self.mem_utils.getSigned(ueax)
            if eax <= 0:
                self.lgr.debug('error return from clone? %d' % eax)
                self.context_manager.genDeleteHap(self.exitHap)
            self.child_pid = eax
            self.lgr.debug('cloneChild exitHap in parent, child will be %d' % eax)
            self.context_manager.addTask(eax)
        elif self.child_pid == pid:
            self.lgr.debug('cloneChild exitHap in child %d' % self.child_pid)
            self.context_manager.genDeleteHap(self.exitHap)
            self.exitHap = None
            SIM_break_simulation('in child %d' % pid)
            self.top.skipAndMail()
        elif self.child_pid is None:
            self.lgr.debug('cloneChild exitHap wrong pid %d child is None' % pid)
        else:
            self.lgr.debug('cloneChild exitHap wrong pid %d not yet return from parent %d' % (pid, self.pid))
