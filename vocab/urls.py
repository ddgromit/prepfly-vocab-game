from django.conf.urls.defaults import *
urlpatterns = patterns('vocab.views',
    (r'vocab/?$','vocab_home_facebook'),
    (r'vocab_facebook/?$','vocab_home_facebook'),
    (r'vocab/game/([0-9]+)/$','game_facebook'),
    (r'vocab/game_facebook/([0-9]+)/$','game_facebook'),
    (r'vocab/iframetest/$','iframetest'),
    
)
urlpatterns += patterns('vocab.api',
    (r'vocab/api/current_words/','current_words_handler'),
    (r'vocab/api/update_skills/','update_skills_handler'),
    (r'vocab/api/reset_level/','reset_level_handler'),
    (r'vocab/api/reset_everything/','reset_everything_handler'),

    (r'vocab/api/user_high_scores/','user_high_scores'),
    (r'vocab/api/friend_high_scores/','friend_high_scores'),
    (r'vocab/api/all_high_scores/','all_high_scores'),
    (r'vocab/api/add_score/','add_score'),
)
