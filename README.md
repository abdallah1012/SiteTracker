# SiteTracker
checks for changes in certain elements each {time} and then sends an email if anything changed which contains an html file of the differences

You will need to use a gmail account, and generate an app password from the security settings in your google account to use as password in the code.

self.tags will contain all the tags to look for differences for and self.tagExceptions lists of tags corresponding in order to the self.tags and are the tags which should be ignored when checking for differences, this is to help against detecting randomness
