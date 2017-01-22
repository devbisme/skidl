def edit_config(name, value)
  config = File.read('_config.yml')
  regexp = Regexp.new('(^\s*' + name + '\s*:\s*)(\S+)(\s*)$')
  config.sub!(regexp,'\1'+value+'\3')
  File.open('_config.yml', 'w') {|f| f.write(config)}
end

  namespace :env do
    desc 'Sets the configuration for development mode.'
    task :dev do
      edit_config 'url', 'http://localhost:4000'
    end

    desc 'Sets the configuration for production mode.'
    task :pro do
      edit_config 'url', '/Notepad'
    end
  end 

  # adapted from https://github.com/imathis/octopress/blob/master/Rakefile   
  # usage rake new_post['My New Post'] or rake new_post (defaults to "My New Post")
  desc "Start a new post"
  task :new, :title do |t, args|
   args.with_defaults(:title => 'My New Post')
   title = args.title
   filename = "_posts/#{Time.now.strftime('%Y-%m-%d')}-#{title.downcase.gsub(/&/,'and').gsub(/[,'":\?!\(\)\[\]]/,'').gsub(/[\W\.]/, '-').gsub(/-+$/,'')}.md"
   puts "Creating new post: #{filename}"
   open(filename, 'w') do |post|
     post.puts "---"
     post.puts "layout: post"
     post.puts "title: \"#{title.gsub(/&/,'&amp;')}\""
     post.puts "description: "
     post.puts "headline: "
     post.puts "modified: #{Time.now.strftime('%Y-%m-%d %H:%M:%S %z')}"
     post.puts "category: personal"
     post.puts "tags: []"
     post.puts "imagefeature: "
     post.puts "mathjax: "
     post.puts "chart: "
     post.puts "comments: true"
     post.puts "featured: false"
     post.puts "---"
   end
  end

  # adapted from https://github.com/imathis/octopress/blob/master/Rakefile   
  # usage rake new_post['My New Post'] or rake new_post (defaults to "My New Post")
  desc "Start a new page"
  task :newpage, :title do |t, args|
   args.with_defaults(:title => 'My New page')
   title = args.title
   filename = "#{title.downcase.gsub(/&/,'and').gsub(/[,'":\?!\(\)\[\]]/,'').gsub(/[\W\.]/, '-').gsub(/-+$/,'')}.md"
   puts "Creating new page: #{filename}"
   open(filename, 'w') do |post|
     post.puts "---"
     post.puts "layout: page"
     post.puts "permalink: #{title.downcase.gsub(/&/,'and').gsub(/[,'":\?!\(\)\[\]]/,'').gsub(/[\W\.]/, '-').gsub(/-+$/,'')}/index.html"
     post.puts "title: \"#{title.gsub(/&/,'&amp;')}\""
     post.puts "description: "
     post.puts "headline: "
     post.puts "modified: #{Time.now.strftime('%Y-%m-%d %H:%M:%S %z')}"
     post.puts "tags: []"
     post.puts "imagefeature: "
     post.puts "mathjax: "
     post.puts "chart: "
     post.puts "comments: true"
     post.puts "---"
   end
  end