from transitions import Machine


class WpsStateMachine(Machine):
    """
    This state machine monitors the output ... TODO
    """

    initial = 'initialization'

    states = ['initialization', 'domain_processing', 'done', 'error']

    transitions = [
        {
            'trigger':      'process_line',
            'source':       '*',
            'dest':         'error',
            'conditions':   'is_error_line'
        },
        {
            'trigger':      'process_line',
            'source':       'initialization',
            'dest':         'domain_processing',
            'conditions':   'is_domain_processing_line',
            'after':        'update_current_domain'
        },
        {
            'trigger':      'process_line',
            'source':       'initialization',
            'dest':         'initialization'
        },
        {
            'trigger':      'process_line',
            'source':       'domain_processing',
            'dest':         'domain_processing',
            'conditions':   'is_domain_processing_line',
            'after':        'update_current_domain'
        },
        {
            'trigger':      'process_line',
            'source':       'domain_processing',
            'dest':         'done',
            'conditions':   'is_finished_line',
            'after':        'finish_current_domain'
        },
        {
            'trigger':      'process_line',
            'source':       'domain_processing',
            'dest':         'domain_processing'
        },
        {
            'trigger':      'process_line',
            'source':       'done',
            'dest':         'done'
        }
    ]

    def __init__(self,
                 max_domains, 
                 check_progress,
                 check_finish,
                 check_error,
                 progress_cb=None):

        Machine.__init__(self, states=WpsStateMachine.states, initial=WpsStateMachine.initial,
                         transitions=WpsStateMachine.transitions)

        self.check_progress = check_progress
        self.check_finish = check_finish
        self.check_error = check_error

        self.progress_cb = progress_cb
        self.max_domains = max_domains
        self.reset()

    def is_domain_processing_line(self, line):
        return self.check_progress(line) is not None

    def is_finished_line(self, line):
        return self.check_finish(line)

    def is_error_line(self, line):
        return self.check_error(line)

    def update_current_domain(self, line):
        self.current_domain, self.max_domains = self.check_progress(line)
        self.call_progress_callback()

    def finish_current_domain(self, line):
        self.current_domain = self.max_domains
        self.call_progress_callback()

    def reset(self):
        self.current_domain = 0
        self.to_initialization()

    def call_progress_callback(self):
        if self.progress_cb:
            self.progress_cb(self.current_domain, self.max_domains)
