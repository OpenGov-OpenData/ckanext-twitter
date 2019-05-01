ckan.module('confirm-tweet', function ($, _) {
                var self;

                return {
                    initialize: function () {
                        self                      = this;
                        self.options.disable_edit = self.options.disable_edit === 'True';
                        self.sandbox.client.getTemplate('edit_tweet.html', self.options, self._onReceiveSnippet);
                    },

                    _onReceiveSnippet: function (html) {
                        var sendUrl  = '/dataset/' + self.options.pkgid + '/tweet';
                        var clearUrl = '/dataset/' + self.options.pkgid + '/tweet-clear';
                        self.modal   = $(html);
                        var form     = self.modal.find('#edit-tweet-form');
                        form.submit(function (e) {
                            e.preventDefault();

                            $.post(sendUrl,
                                form.serialize(),
                                    function (results) {
                                        self.modal.modal('hide');
                                        if (results === undefined || results === null) {
                                            self.flash_error('Tweet not posted due to unknown error.');
                                        }
                                        else if (!results.success) {
                                            self.flash_error('Tweet not posted! Error message: "' + results.reason + '".<br>Your tweet: "' + results.tweet + '".');
                                        }
                                        else {
                                            self.flash_success('Tweet posted!<br>Your tweet: "' + results.tweet + '"')
                                        }
                                    },
                                    'json'
                                );
                        });

                        let cancelButton = self.modal.find('#edit-tweet-cancel');
                        cancelButton.click(function(e) {
                            $.post(clearUrl,
                                {},
                                function() {
                                    self.modal.modal('hide');
                                });
                        });

                        self.modal.modal().appendTo(self.sandbox.body);
                    },

                    flash: function (message, category) {
                        $('.flash-messages')
                            .append('<div class="alert ' + category + '">' + message + '</div>');
                    },

                    flash_error: function (message) {
                        this.flash(message, 'alert-error');
                    },

                    flash_success: function (message) {
                        this.flash(message, 'alert-success');
                    }
                }
            }
);